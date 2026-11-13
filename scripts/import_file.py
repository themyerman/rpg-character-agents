#!/usr/bin/env python3
"""
Import an outside file (a party or location brief) into the app's trusted set.

The app strips the prose out of any loaded file it can't vouch for, so external
material you actually want to use — an old campaign writeup, a brief a friend
sent, text pulled from a PDF — would otherwise come back as a bare skeleton. This
is the human-in-the-loop way in: it shows you the file, screens it, and makes you
explicitly vouch for it before recording it as trusted (see lib/importer.py).

    python scripts/import_file.py path/to/brief.md
    python scripts/import_file.py path/to/brief.md --game dnd --kind party

With --game / --kind omitted you'll be prompted for them.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import importer

OUTPUT = ROOT / "output"


def _prompt_choice(label: str, options: list[str]) -> str:
    print(f"\n{label}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  Pick a number from the list.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import an outside brief into the trusted set.")
    parser.add_argument("file", help="path to the file to import")
    parser.add_argument("--game", choices=sorted(importer.GAME_SUBDIRS), help="game system")
    parser.add_argument("--kind", choices=sorted(importer.KIND_SUBFOLDERS), help="party or location")
    args = parser.parse_args()

    src = Path(args.file)
    if not src.is_file():
        print(f"error: no such file: {src}", file=sys.stderr)
        return 2

    game = args.game or _prompt_choice("Which game is this for?", sorted(importer.GAME_SUBDIRS))
    kind = args.kind or _prompt_choice("What kind of brief is it?", sorted(importer.KIND_SUBFOLDERS))

    saved = importer.run_import(src, OUTPUT, game, kind)
    return 0 if saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
