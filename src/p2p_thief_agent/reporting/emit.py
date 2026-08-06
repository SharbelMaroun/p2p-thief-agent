"""Persist an artifact so a crash cannot leave half of one (`M7-011`).

The row's condition names the failure exactly: "a crash mid-write cannot leave a
half-written artifact that later fails audit". That is a worse outcome than no file at
all, because it is **silent** — the process dies, the file looks present, and the problem
surfaces days later during grading, by which time rule 19's audit phase reads a truncated
document as a technical mismatch. Its sanction is "score of 0 for the falsifying group",
and nothing in the artifact distinguishes a truncated write from a deliberate one.

So the write goes to a temporary file **in the same directory** and is swapped in with
`os.replace`: the visible file is either the old one or the complete new one, never a
prefix. Same-directory matters — `os.replace` is atomic only within a filesystem, so a
temp file under the system temp directory would silently degrade to a copy-then-rename
and reintroduce the window this exists to close.

Emission holds no socket and no peer state, so a game that ends because the opponent
vanished still produces its artifacts. That is the only way the files can be evidence of a
game that went *wrong*.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path


class EmitError(OSError):
    """Raised when an artifact cannot be written where it was asked to go."""


def artifact_bytes(artifact: Mapping[str, object]) -> bytes:
    """Serialize exactly as the file will sit on disk.

    Sorted keys and `ensure_ascii=False` to match the canonicalization the hashes use, so
    a reader who re-serializes gets the same bytes. A trailing newline because these are
    committed to a repository, where a file without one is a permanent diff nuisance.
    """
    text = json.dumps(dict(artifact), sort_keys=True, ensure_ascii=False, indent=2)
    return (text + "\n").encode("utf-8")


def write_artifact(directory: Path, filename: str, artifact: Mapping[str, object]) -> Path:
    """Write one artifact atomically and return the path it now occupies.

    Refuses a filename carrying a directory component. Every caller derives its name from
    `reporting.naming`, and a name that could climb out of the artifact directory would
    mean a negotiated `game_id` had reached the filesystem unchecked.
    """
    if "/" in filename or "\\" in filename or filename in {"", ".", ".."}:
        raise EmitError(f"artifact filename {filename!r} must be a bare name")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    payload = artifact_bytes(artifact)
    handle, temporary = tempfile.mkstemp(dir=str(directory), prefix=f".{filename}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())  # the bytes, not just the buffer, before the swap
        destination = directory / filename
        os.replace(temporary, destination)
    except OSError:
        Path(temporary).unlink(missing_ok=True)
        raise
    return destination


def write_all(directory: Path, artifacts: Mapping[str, Mapping[str, object]]) -> dict[str, Path]:
    """Write a whole set, keyed by filename. Order is irrelevant; each write is atomic."""
    return {name: write_artifact(directory, name, body) for name, body in artifacts.items()}
