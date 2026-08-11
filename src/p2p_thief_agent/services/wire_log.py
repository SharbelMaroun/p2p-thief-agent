"""Record what actually arrived on the wire, because the access log does not (`M9-042`).

**Why this exists.** On 2026-08-11 an offer from group `uoh-ay26` reached this peer and
vanished. All we had afterwards was uvicorn's access log — a column of `200 OK` — which is
the same thing it prints for a call that succeeded, a call naming a tool we do not have, and
a call whose argument name is wrong. Reconstructing the cause took an hour of reproducing the
failure locally, and the answer was never recoverable from anything we had stored.

Three facts made that possible, and this module addresses the third:

* an MCP tool error is an application-level result, so the HTTP layer still reports `200`;
* our tools acknowledge on **enqueue**, while validation happens later at drain, so accept
  and reject are separated in time from the request that caused them;
* nothing anywhere wrote either of them down. The game log records the *match*; it has never
  recorded the *conversation*, and rule 36's mutual audit is an argument about the
  conversation.

**Append-only JSONL, one line per event, no rotation.** A match is minutes long and a line is
tiny, so a rotating handler would add failure modes to buy nothing. Lines are flushed as they
are written: this file is read after a crash, and a buffered line is exactly the one worth
having.

**It cannot break a match.** Every failure — unwritable directory, full disk, encoding
problem — is swallowed. Logging that can refuse a turn is worse than no logging, and rule 6
makes a frozen peer a technical loss. `enable` returning `False` is the only signal, and
nothing acts on it.

Deliberately *not* here: message bodies. A turn payload carries the sealed commitment and,
after reveal, the nonce; writing those to an unmanaged file is a rule-18/39 hazard for a
diagnostic nobody needs. Tool name, verdict, reason and size answer the question that cost us
the hour; the payload never came into it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path

_target: Path | None = None


def enable(directory: str | Path, name: str = "wire.jsonl") -> bool:
    """Point the log at `directory/name`, creating the directory. Never raises."""
    global _target  # noqa: PLW0603 - one process, one wire log; a handle would be ceremony
    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        _target = path / name
        return True
    except OSError:
        _target = None
        return False


def disable() -> None:
    """Stop recording. Used by tests so one test's log never reaches another's file."""
    global _target  # noqa: PLW0603
    _target = None


def target() -> Path | None:
    """The file currently being written, or `None` when logging is off."""
    return _target


def record(event: str, **fields: object) -> None:
    """Append one event. Silent when disabled, and silent on any write failure."""
    if _target is None:
        return
    line = {"at": datetime.now(UTC).isoformat(), "event": event, **fields}
    try:
        with _target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n")
    except (OSError, TypeError, ValueError):
        return


def received(tool: str, message: object, *, queued: bool) -> None:
    """A tool was invoked and the message was enqueued, or refused for a full inbox.

    `queued=False` is `AE-29`'s bounded-inbox refusal, which the opponent is told about in
    the tool response — recording it here is what lets us prove we said so.
    """
    record("received", tool=tool, queued=queued, keys=_keys(message))


def validated(tool: str, *, accepted: bool, reason: object = None) -> None:
    """A drained message passed or failed this peer's validation.

    The `reason` is the whole point. It is computed today, put in a `Delivery`, and then
    discarded by every caller that is not the turn loop.
    """
    record("validated", tool=tool, accepted=accepted,
           reason=None if reason is None else str(reason))


def _keys(message: object) -> list[str]:
    """Top-level field names only — enough to spot a shape mismatch, no payload."""
    return sorted(str(key) for key in message) if isinstance(message, Mapping) else []
