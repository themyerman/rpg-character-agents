"""
Human-in-the-loop import of outside material into the app's trusted set.

The structural defense (lib.safety.extract_safe) strips the prose out of every
loaded file the app can't vouch for (see lib.provenance), so a planted command
can't ride a reused file into a later prompt. The cost is that genuinely external
material you actually *want* to use — a paragraph a friend sent, an old campaign
writeup, the text of a PDF — comes back as a bare skeleton too, because it has no
provenance hash. There is no fingerprint, so the app can't tell your hand-built
backstory from an injection, and it treats both the same: strip to structure.

This module is the sanctioned way back in. It does NOT try to judge whether the
content is safe — the whole point of the study behind this app is that you can't
reliably compute "is this text dangerous?". Instead it puts a human in the loop:

    1. show the file in full,
    2. surface any automated injection/length warnings,
    3. require an explicit, informed confirmation,
    4. only then record the content as trusted (its hash goes in the manifest)
       and save it under output/ where the agents load it — with full prose,
       because now the app vouches for it on your say-so.

The trust decision is a human's, and a human can be talked into vouching for the
wrong file. That is deliberate, and it is a *smaller, visible* attack surface than
silently trusting every loaded file: it happens once, in the open, with the whole
text in front of you — not invisibly on every run. If you don't vouch, nothing is
trusted and nothing is saved.
"""

from pathlib import Path

from lib import provenance
from lib.safety import screen_saved
from lib.utils import slug

# Game key -> output/ subdirectory (mirrors agents/event_agent.GAME_SUBDIRS).
GAME_SUBDIRS: dict[str, str] = {
    "dnd": "dnd",
    "traveller": "traveller",
    "firefly": "firefly",
    "scum": "scum_villainy",
    "alien": "alien",
    "deadlands": "deadlands",
}

# Importable kinds -> the subfolder the agents load them from.
# Only kinds the agents actually read back as context are importable; importing
# a file the app never loads would trust it for nothing.
KIND_SUBFOLDERS: dict[str, str] = {
    "party": "parties",
    "location": "locations",
}

CONFIRM_WORD = "trust"


def dest_dir(game: str, kind: str) -> str:
    """The output-relative directory an imported {game} {kind} belongs in."""
    if kind not in KIND_SUBFOLDERS:
        raise ValueError(f"unknown import kind: {kind!r} (expected one of {sorted(KIND_SUBFOLDERS)})")
    subdir = GAME_SUBDIRS.get(game, game)
    return f"{subdir}/{KIND_SUBFOLDERS[kind]}"


def _target_path(output_root, dest_subdir: str, source_name: str) -> Path:
    """A non-clobbering .md path under <output_root>/<dest_subdir> for an import."""
    directory = Path(output_root) / dest_subdir
    stem = slug(Path(source_name).stem) or "imported"
    name = f"{stem}-imported.md"
    path = directory / name
    counter = 2
    while path.exists():
        path = directory / f"{stem}-imported-{counter}.md"
        counter += 1
    return path


def review(content: str) -> list[str]:
    """Automated warnings a human should see before vouching for `content`.

    Thin wrapper over the same write-boundary screen a generated file gets, so an
    imported file is held to at least the standard the app's own output is. An
    empty list does NOT mean 'safe' — it means nothing automated fired, and the
    human is still the real check.
    """
    return screen_saved(content)


def commit(output_root, content: str, dest_subdir: str, source_name: str) -> Path:
    """Save vouched `content` under output/ and record it as trusted.

    Separated from the interactive flow so it can be driven and tested directly.
    Recording the hash is what lets later loads keep the file's full prose.
    """
    path = _target_path(output_root, dest_subdir, source_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    provenance.record(output_root, content)
    return path


def run_import(
    source,
    output_root,
    game: str,
    kind: str,
    *,
    input_fn=input,
    echo=print,
) -> Path | None:
    """Interactive review-screen-vouch import of `source` into the trusted set.

    Reads the file, shows it in full, prints any automated warnings, then requires
    the human to type the confirmation word. On confirmation the content is saved
    under output/ and recorded as trusted (full prose on reload). Returns the saved
    path, or None if the human declined or the kind is unknown.

    I/O is injected (`input_fn`, `echo`) so the flow is testable without a TTY.
    """
    src = Path(source)
    try:
        subdir = dest_dir(game, kind)
    except ValueError as exc:
        echo(f"  [import] {exc}")
        return None

    content = src.read_text(encoding="utf-8")

    echo(f"\n----- {src.name} ({len(content):,} chars) -----")
    echo(content)
    echo("----- end of file -----\n")

    warnings = review(content)
    if warnings:
        echo("Automated safety warnings — read these carefully:")
        for w in warnings:
            echo(f"  [safety] {w}")
    else:
        echo("No automated warnings fired — but that is not a clean bill of health. "
             "You are the check. Read the file above before you vouch for it.")

    echo(
        "\nImporting marks this file as TRUSTED. A trusted file keeps its full text "
        "when it is loaded into a generation — including anything hidden in its prose. "
        "Only vouch for a file you have read and whose source you trust."
    )
    answer = input_fn(f"Type '{CONFIRM_WORD}' to import, anything else to cancel: ").strip().lower()
    if answer != CONFIRM_WORD:
        echo("Cancelled — nothing imported, nothing trusted.")
        return None

    path = commit(output_root, content, subdir, src.name)
    echo(f"Imported and trusted: {path}")
    return path
