"""
Shared utilities for all RPG character generators.

Centralises the three patterns that were copy-pasted across every agent:
  - run_agent_loop  — the Anthropic tool-use while loop
  - save_character  — slugify heading → write to {subdir}/characters/
  - strip_preamble  — remove any text before the first ## heading

Also keeps the pick() UI helper that was already here.
"""

import re
import unicodedata
from pathlib import Path

import anthropic


# ── Anthropic client (singleton) ──────────────────────────────────────────────

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


# ── UI helpers ─────────────────────────────────────────────────────────────────

def pick(prompt: str, options: list[tuple[str, str]], default_idx: int = 0) -> str:
    """Display a numbered menu and return the selected key.
    Defaults to options[default_idx] on empty or invalid input."""
    print(f"\n{prompt}")
    for i, (_, label) in enumerate(options, 1):
        suffix = "  (default)" if i - 1 == default_idx else ""
        print(f"  {i}. {label}{suffix}")
    raw = input("> ").strip()
    if raw:
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
        except ValueError:
            pass
    return options[default_idx][0]


# ── Text helpers ───────────────────────────────────────────────────────────────

def strip_preamble(text: str) -> str:
    """Remove any introductory text before the first ## heading."""
    lines = text.strip().splitlines()
    idx   = next((i for i, l in enumerate(lines) if l.startswith("##")), 0)
    return "\n".join(lines[idx:])


def slug(text: str) -> str:
    """Lowercase, transliterate accented/diacritic chars, collapse non-alphanumeric runs to dashes.

    Uses NFKD decomposition to strip combining marks so accented characters
    map to their base letter (é→e, š→s, ȟ→h, á→a). Characters that don't
    decompose this way (e.g. ŋ, ø, æ) fall back to a dash.
    """
    normalized = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")


# ── Agentic loop ───────────────────────────────────────────────────────────────

def run_agent_loop(
    prompt: str,
    system: str,
    tools: list,
    run_tool_fn,
    detect_phase_fn=None,
    phase_messages: dict | None = None,
    max_tokens: int = 4096,
) -> str:
    """Generic Anthropic tool-use loop.

    When detect_phase_fn and phase_messages are both supplied, prints a blank
    line before the first tool call and a progress line each time the phase
    changes.  Omit both (or pass None) for silent operation — useful for
    sub-agent calls inside npc_cluster_agent.
    """
    client   = get_client()
    messages = [{"role": "user", "content": prompt}]
    seen     = set()
    phase    = None
    verbose  = bool(detect_phase_fn and phase_messages)

    if verbose:
        print()

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        new_phase = detect_phase_fn(block.name, seen)
                        if new_phase and new_phase != phase:
                            phase = new_phase
                            print(phase_messages[phase])

                    seen.add(block.name)
                    result = run_tool_fn(block.name, block.input)
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result,
                    })

            messages.append({"role": "user", "content": tool_results})


# ── Save helper ────────────────────────────────────────────────────────────────

def save_character(
    content: str,
    mode: str,
    subdir: str,
    root: str | Path,
    output_type: str = "characters",
) -> Path:
    """Save output to output/{subdir}/{output_type}/{name-slug}-{mode}.md

    output_type controls the subfolder: "characters", "aliens", "synthetics",
    "first-contact", etc. Defaults to "characters" for backward compatibility.

    Handles ## heading extraction, slugification, and collision counters.
    root should be the project root directory (pass Path(__file__).parent.parent
    from agents in the agents/ subdirectory, or Path(__file__).parent from root-level scripts).
    """
    first_line = next(
        (l for l in content.strip().splitlines() if l.startswith("##")),
        content.strip().splitlines()[0],
    )
    name_raw  = re.sub(r"[#*]", "", first_line).strip()
    name_slug = slug(name_raw)
    filename  = f"{name_slug}-{mode}.md"

    output_dir = Path(root) / "output" / subdir / output_type
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    if filepath.exists():
        stem    = filepath.stem
        counter = 2
        while filepath.exists():
            filepath = output_dir / f"{stem}-{counter}.md"
            counter  += 1

    filepath.write_text(content)
    return filepath
