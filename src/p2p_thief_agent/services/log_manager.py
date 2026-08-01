"""The Log Manager subsystem: an append-only, per-match structured log (`M5-008`).

Book chapter 9 lists the Log Manager as one of the orchestrator's five subsystems. It
records every sent and received message, every phase transition, and every commitment,
in order and in enough detail to reconstruct the match for the end-of-game mutual audit
(`AE-36`). Three properties are load-bearing:

- **Append-only** (`M5-008c`): there is no method that edits or deletes a prior entry,
  the file is opened in append mode, and ``entries`` hands back a copy — so the record
  can only ever grow. A tampered log is worthless as audit evidence.
- **Per-match path** (`M5-008d`): the file name carries the ``game_uid``, so two matches
  never overwrite each other, and reopening the same match appends rather than truncates
  (the recovery path after a watchdog shutdown).
- **Nonce secrecy** (`M5-008b`, `AE-18`): a commitment is logged when it is made, but the
  nonce that opens it is withheld until ``open_audit`` is called after the final reveal.
  ``reveal_nonce`` raises before then, so the log cannot leak a nonce early by mistake.

``record_transition`` is shaped to be passed straight to ``run_turn``'s ``on_transition``
hook (`M5-007d`). Time is injected, the same discipline the deadline and watchdog
services follow.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path


class LogError(RuntimeError):
    """Raised on an illegal log operation, e.g. revealing a nonce before the audit."""


class LogManager:
    """Append-only, per-match structured match log."""

    __slots__ = ("_path", "_clock", "_entries", "_seq", "_audit_open")

    def __init__(
        self,
        game_uid: str,
        directory: str | Path,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if not game_uid:
            raise LogError("game_uid is required so matches never share a log")
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self._path = directory / f"log_{game_uid}.jsonl"
        self._clock = clock
        self._entries: list[dict] = []
        # Continue the sequence after a reopen, so recovery keeps a monotonic count.
        self._seq = self._existing_line_count()
        self._audit_open = False

    def _existing_line_count(self) -> int:
        if not self._path.exists():
            return 0
        with self._path.open(encoding="utf-8") as handle:
            return sum(1 for _ in handle)

    @property
    def path(self) -> Path:
        """Return the per-match log file path."""
        return self._path

    @property
    def entries(self) -> tuple[dict, ...]:
        """Return an immutable view of the entries this instance appended."""
        return tuple(self._entries)

    @property
    def audit_open(self) -> bool:
        """Return whether the audit is open (revealed nonces may then be logged)."""
        return self._audit_open

    def record_sent(self, message: dict) -> dict:
        """Log an outbound message."""
        return self._append("sent", message=message)

    def record_received(self, message: dict) -> dict:
        """Log an inbound message."""
        return self._append("received", message=message)

    def record_transition(self, phase: object) -> dict:
        """Log a phase transition, storing the phase's value."""
        return self._append("transition", phase=getattr(phase, "value", phase))

    def record_commitment(self, step: int, commit: str) -> dict:
        """Log a commitment; the nonce that opens it is withheld until the audit."""
        return self._append("commitment", step=step, commit=commit)

    def open_audit(self) -> None:
        """Open the audit, after which revealed nonces may be logged (`AE-18`)."""
        self._audit_open = True

    def reveal_nonce(self, step: int, nonce: str) -> dict:
        """Log a revealed nonce, but only once the audit is open (`AE-18`)."""
        if not self._audit_open:
            raise LogError("a nonce cannot be logged before the audit is opened (AE-18)")
        return self._append("nonce", step=step, nonce=nonce)

    def _append(self, kind: str, **data: object) -> dict:
        """Append one entry to memory and to the append-only file, and return it."""
        entry = {"seq": self._seq, "timestamp": self._clock(), "kind": kind, **data}
        self._seq += 1
        self._entries.append(entry)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry
