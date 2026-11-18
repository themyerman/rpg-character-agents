"""
Schema-based allowlist for loaded briefs — the strict, typed replacement for the
generic structural strip (lib.safety.extract_safe).

Background. Loaded files are an injection vector (see lib.safety / lib.provenance):
a saved brief is read back into a later prompt, so a directive planted in one can
hijack the next generation. `extract_safe` defends by *shape* — it keeps any line
that looks like a heading, a bullet, or a bold label and drops the rest. That kills
plain-prose injection, but it keeps the *whole* line once a shape matches, so an
attacker who dresses the directive as a bullet or an invented `**Label:**` gets a
line through.

This module is the stronger layer: **default-deny by schema.** Each brief type we
emit has a known set of sections, and each section has an expected value *type* and
a *length* bound. On load we parse the file against that schema and keep only known
sections, each clamped to its type and cap. An invented section ("### SYSTEM
OVERRIDE", "**GM directive:** …") matches no field, so it is dropped wholesale —
not because it looked dangerous, but because it isn't on the allowlist.

The schemas here are derived from what the generators actually emit (see
agents/party_agent.py and agents/location_agent.py output templates), so a real,
unedited brief of the right type passes through intact.

Honest residual. An allowlist of section *names* plus a length cap does not sanitize
a section's *value*: a short directive hidden inside the prose of a legitimate field
(e.g. "The Fault Line") is still admitted, capped. The schema shrinks the attack
surface from "any shape-valid line anywhere" to "inside the value of one known field,
under a length bound" — a much smaller, much more conspicuous place to hide. The
remaining gap is closed by the other layers: provenance (trust only our own
unmodified files) and human import (a person vouches for a foreign file before it is
trusted). The only total seal is never feeding untrusted text to the model at all.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    canonical: str          # the heading we re-emit
    aliases: tuple          # accepted headings (normalized match), canonical included
    kind: str               # "prose" | "bullets"
    max_chars: int          # length bound for this field's value


@dataclass(frozen=True)
class BriefSchema:
    brief_type: str
    title_max: int
    fields: tuple           # tuple[Field, ...] in emit order

    def lookup(self, normalized_heading: str):
        for f in self.fields:
            if normalized_heading in f.aliases:
                return f
        return None


def _norm(heading: str) -> str:
    """Normalize a heading for allowlist matching: strip markdown, lowercase,
    collapse to letters/digits/spaces."""
    h = re.sub(r"[*`_#]", "", heading)
    h = re.sub(r"[^a-z0-9 ]", "", h.lower())
    return re.sub(r"\s+", " ", h).strip()


def _a(*names: str) -> tuple:
    return tuple(_norm(n) for n in names)


# ── Schemas (derived from the generators' own output templates) ─────────────────

PARTY = BriefSchema(
    brief_type="party",
    title_max=120,
    fields=(
        Field("Members", _a("Members", "Crew", "Posse", "Roster"), "bullets", 4000),
        Field("How They Came Together",
              _a("How They Came Together", "How They Met"), "prose", 2500),
        Field("What Holds Them Together", _a("What Holds Them Together"), "prose", 1800),
        Field("The Fault Line", _a("The Fault Line"), "prose", 1800),
        Field("Shared Secret", _a("Shared Secret"), "prose", 1800),
        Field("First Session Hook",
              _a("First Session Hook", "First Score Hook", "GM Hook", "GM Hooks"),
              "prose", 2200),
    ),
)

LOCATION = BriefSchema(
    brief_type="location",
    title_max=120,
    fields=(
        Field("Atmosphere", _a("Atmosphere"), "prose", 1800),
        Field("Notable NPCs", _a("Notable NPCs", "NPCs"), "prose", 2200),
        Field("The Situation", _a("The Situation", "Situation"), "prose", 2200),
        Field("Hooks", _a("Hooks"), "prose", 2200),
        Field("GM Notes", _a("GM Notes", "GM Note"), "prose", 2200),
    ),
)

SCHEMAS = {s.brief_type: s for s in (PARTY, LOCATION)}


# ── Value clamping by type ──────────────────────────────────────────────────────

_BULLET = ("-", "*", "+", "•")


def _clamp_value(body_lines: list, field: Field) -> str:
    if field.kind == "bullets":
        kept = [ln for ln in body_lines if ln.strip().startswith(_BULLET)]
    else:  # prose: drop stray heading lines (an injected sub-heading won't ride in)
        kept = [ln for ln in body_lines if not ln.strip().startswith("#")]
    value = "\n".join(kept).strip()
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value[: field.max_chars].rstrip()


# ── Extraction ──────────────────────────────────────────────────────────────────

def _parse(text: str, schema: BriefSchema):
    """Parse `text` into (title, sections). Each section is a dict with the matched
    schema Field (or None for an unknown heading), the raw heading, and its body
    lines. Shared by extract and validate so they agree on structure."""
    title = None
    sections = []
    cur = None
    for ln in text.splitlines():
        m = re.match(r"^(#{2,6})\s+(.*)$", ln)
        if m:
            level, head = len(m.group(1)), m.group(2)
            if level == 2 and title is None:
                title = re.sub(r"[*`]", "", head).strip()
                cur = None
                continue
            if level == 3:
                cur = {"field": schema.lookup(_norm(head)), "raw": head.strip(), "body": []}
                sections.append(cur)
                continue
            # level 4+ headings fall through into the current section's body
        if cur is not None:
            cur["body"].append(ln)
        # lines before the first section (and the title line) are dropped
    return title, sections


def extract_by_schema(text: str, schema: BriefSchema) -> str:
    """Rebuild `text` keeping only the schema's known sections, each clamped to its
    declared type and length. Unknown sections are dropped entirely. The title (the
    first level-2 `##` heading) is kept, capped to `title_max`."""
    title, sections = _parse(text, schema)
    out = []
    if title:
        out.append(f"## {title[: schema.title_max]}")
    for field in schema.fields:                      # emit in schema order
        for sec in sections:
            if sec["field"] is field:
                value = _clamp_value(sec["body"], field)
                if value:
                    out.append(f"### {field.canonical}\n{value}")
                break
    return "\n\n".join(out)


def validate(brief_type: str, text: str) -> list:
    """Check that a brief CONFORMS to its schema. Returns a list of warning strings
    (empty = clean). This is the check for our *own* generated output: every file the
    tool emits should pass, so a trusted brief and a stripped untrusted copy carry the
    same structure. Unschemad types return [] (nothing to check).

    Warns on: a missing title, a missing expected field, an unknown section (a heading
    not on the allowlist), and a value over its length cap.
    """
    schema = SCHEMAS.get(brief_type)
    if schema is None:
        return []
    title, sections = _parse(text, schema)
    warnings = []
    if not title:
        warnings.append("missing title (no '## ' heading)")
    elif len(title) > schema.title_max:
        warnings.append(f"title exceeds {schema.title_max} chars")

    present = {sec["field"] for sec in sections if sec["field"] is not None}
    for field in schema.fields:
        if field not in present:
            warnings.append(f"missing section: {field.canonical}")
    for sec in sections:
        if sec["field"] is None:
            warnings.append(f"unknown section not in schema: {sec['raw']!r}")
        else:
            body = "\n".join(sec["body"]).strip()
            if len(body) > sec["field"].max_chars:
                warnings.append(
                    f"section {sec['field'].canonical!r} is {len(body)} chars "
                    f"(cap {sec['field'].max_chars})"
                )
    return warnings


def extract(brief_type: str, text: str) -> str:
    """Dispatch: schema-extract a known brief type; otherwise fall back to the
    generic structural strip so an unschemad type (e.g. a character sheet) still
    gets a defense."""
    schema = SCHEMAS.get(brief_type)
    if schema is None:
        from lib.safety import extract_safe
        return extract_safe(text)
    return extract_by_schema(text, schema)
