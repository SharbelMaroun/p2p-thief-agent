"""Loading a log for replay — including one this repository did not write (`M8-012`).

**The foreign log is the requirement, not a bonus.** Rule 36 mandates a "comprehensive
mutual log audit" at the end of every match as a necessary condition for agreement
(p.131/276), and p.39/102 spells it out: "each side presents its full log … each side
reconstructs the opponent's data through the revealed nonces". A verifier fed only its own
output confirms that this repository's writer agrees with its reader, which it always will.
The reference makes the same move, auto-locating `logs/<opponent_group_id>/log_…json`.

So `load_log` takes **a path and nothing else**. It never consults our identity, our
`game_id`, our key material, or our output directory, and `test_foreign_log.py` holds that
line two ways — by verifying a log built by a stranger's code path, and by parsing this
package's own imports so a future dependency on our identity fails the suite loudly.

**Tolerant about shape, strict about the reveal.** An opponent's log may carry a different
`schema_version`, extra keys, or sections we never emit. Refusing on those grounds would
fail rule 36 over a cosmetic difference and hand a real forger the excuse that our viewer
"could not open" the evidence. What we require is only what verification consumes.

**Not-yet-revealed is not forged.** Rule 18 requires a running log to carry no nonces at
all; calling that `TAMPERED` would accuse an honest peer of the one thing `:1769` gives no
appeal against. That is a load-time refusal with its own error, not a verdict — a peer who
*never* reveals is a settlement question, not a forgery.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


class LogNotReplayableError(ValueError):
    """The file cannot be replayed at all — distinct from replaying to a `TAMPERED`."""


@dataclass(frozen=True)
class ReplayLog:
    """A loaded log and where it came from. `origin` is shown so a screenshot makes clear
    *whose* log produced the banner — the whole point of a mutual audit."""

    origin: str
    document: Mapping[str, object]

    @property
    def records(self) -> Sequence[Mapping[str, object]]:
        records = self.document.get("records")
        return records if isinstance(records, Sequence) else ()  # type: ignore[return-value]

    @property
    def game_id(self) -> object:
        return self.document.get("game_id")

    @property
    def sub_game(self) -> object:
        """The template's key name, with the older one accepted for a foreign log."""
        document = self.document
        return document.get("sub_game_number", document.get("sub_game"))


def parse_log(document: object, origin: str = "<memory>") -> ReplayLog:
    """Accept a parsed document as replayable, or say precisely why it is not (`M8-008c`)."""
    if not isinstance(document, Mapping):
        raise LogNotReplayableError(f"{origin}: top level is not a JSON object")
    records = document.get("records")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)) or not records:
        raise LogNotReplayableError(f"{origin}: no `records` array to replay")
    unrevealed = sum(
        1 for record in records
        if not isinstance(record, Mapping) or "nonce" not in record
    )
    # All of them missing means the game has not ended -- honest, and rule 18 requires it.
    # *Some* missing is a log revealed and then interfered with, so that one goes through
    # to the verifier and comes back TAMPERED rather than being refused here.
    if unrevealed == len(records):
        raise LogNotReplayableError(
            f"{origin}: no record has been revealed; this is an in-play log, not a final "
            "one [AE-18]. A peer who never reveals is a settlement matter, not a forgery."
        )
    return ReplayLog(origin, document)


def load_log(path: str | Path) -> ReplayLog:
    """Read a log from disk for replay. Any readable path — ours or an opponent's."""
    location = Path(path)
    try:
        text = location.read_text("utf-8")
    except OSError as error:  # a missing opponent log is a normal, reportable state
        raise LogNotReplayableError(f"{location}: cannot be read ({error.strerror})") from error
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise LogNotReplayableError(f"{location}: is not valid JSON ({error.msg})") from error
    return parse_log(document, origin=str(location))
