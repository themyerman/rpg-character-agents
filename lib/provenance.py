"""
Provenance for loaded files: let the app recognise its own unmodified output.

The structural defense (lib.safety.extract_safe) is safe but blunt — it strips the
prose out of *every* loaded brief, so reusing your own saved content loses its
flavor. That cost is only worth paying for files the app can't vouch for. A file
the app generated and saved itself, unmodified, is as trustworthy as the run that
made it.

So: when the app saves a brief, it records a hash of the content here. When it
loads one back, it checks the hash. This answers "did I make this, untampered?" —
a yes/no you can compute — instead of "is this content dangerous?", which you
can't. A match means trust it fully (keep the prose). No match (hand-edited, or a
file from somewhere else) means it's untrusted, and the structural strip applies.

The manifest is a plain list of SHA-256 hashes at <output_root>/.provenance.json.
It is advisory and best-effort: every read and write is wrapped so a missing or
unreadable manifest simply means "nothing is trusted" (fail closed — strip).
"""

import hashlib
import json
from pathlib import Path

MANIFEST_NAME = ".provenance.json"


def _manifest_path(output_root) -> Path:
    return Path(output_root) / MANIFEST_NAME


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _load(output_root) -> set:
    try:
        return set(json.loads(_manifest_path(output_root).read_text()))
    except Exception:
        return set()


def record(output_root, content: str) -> None:
    """Mark `content` as the app's own output (call right after saving a file)."""
    hashes = _load(output_root)
    hashes.add(_hash(content))
    try:
        p = _manifest_path(output_root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(sorted(hashes)))
    except Exception:
        pass  # advisory; losing the record just means the file re-reads as untrusted


def is_trusted(output_root, content: str) -> bool:
    """True iff this exact content was saved by the app and hasn't been edited."""
    return _hash(content) in _load(output_root)
