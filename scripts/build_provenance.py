#!/usr/bin/env python3
"""
(Re)build the provenance manifest for the files that ship in output/.

The app trusts a loaded brief — and keeps its full prose — only if it recognizes
the file as its own unmodified output (see lib/provenance.py). Example content
that ships in the repo was generated before that check existed, so without this
step a cloned copy would treat its own shipped examples as untrusted and strip
them on reload. Run this whenever you add or regenerate example content; it is
idempotent.

    python scripts/build_provenance.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import provenance

OUTPUT = ROOT / "output"


def main() -> None:
    files = sorted(p for p in OUTPUT.rglob("*.md"))
    for p in files:
        provenance.record(OUTPUT, p.read_text(encoding="utf-8"))
    manifest = provenance._manifest_path(OUTPUT)
    print(f"Recorded {len(files)} shipped file(s) into {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
