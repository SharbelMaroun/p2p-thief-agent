"""The replay verdict: rule 20's threshold condition (`M8-002b`, `M8-002c`, `M8-002d`).

Appendix E rule 20 is Mandatory, sanction "**Threshold condition** for confirmation of logs
and submission of the project" (p.129/272). Confirmed with the book notebook: the project
cannot be accepted without this. It is the only deliverable here whose absence is a
rejected submission rather than a lost mark.

**Two verdicts, and the second one is fatal.** `:1693` — a green `Verified OK` stamp, or a
red `TAMPERED` banner after which "the replay is immediately invalidated". `:1769` removes
the escape hatch: "no appeal process and no room for manual correction". A third state
would be a state the rules do not have.

**One bad step voids the whole match (`M8-002c`).** The book's own loop returns `TAMPERED`
at the first failure (`:1743`); `:1753` — "If any single step returns `TAMPERED`, the
entire match is invalidated." `DEV-SPEC.md:429` restates it.

**The digest, and only the digest, decides this banner.** Asked directly, rule 19 reads
"Mandatory to technically disqualify a game for any mismatch **in the digest** during the
audit phase" (p.129/271). Structural damage — a gap, a duplicate, a shuffle — is a
different question with a *different sanction* (rule 35, rule 5), so it is reported by
`sequence.py` and deliberately does not flip this banner. Conflating them would report the
wrong rule, and red-bannering an opponent carries no appeal.

**Why not the chapter-7 formula (`M8-002d`).** `:1733` computes `sha256(f"{nonce}|{move}")`;
this repository seals the canonical payload with the nonce. They never agree. That is not a
contradiction: `:1757` footnotes the sketch in the book's own voice as "simplified … for
the sake of the illustration", naming Chapter 5 normative — and `DEV-SPEC.md:435` annotates
its own copy of the listing the same way. `C-016` is reclassified accordingly.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

from p2p_thief_agent.protocol.crypto import CryptoError, verify

REVEAL_FIELDS = ("commit", "payload", "nonce")


class Verdict(str, Enum):
    """The only two outcomes the rules define. `:1707` labels the second "disqualify"."""

    VERIFIED_OK = "Verified OK"
    TAMPERED = "TAMPERED"


@dataclass(frozen=True)
class RecordCheck:
    """One record's outcome, keeping the reason for the banner and the audit trail."""

    index: int
    step: object
    verdict: Verdict
    reason: str

    @property
    def ok(self) -> bool:
        return self.verdict is Verdict.VERIFIED_OK


@dataclass(frozen=True)
class MatchVerdict:
    """The match-level result. `first_bad` is where the book stops the replay."""

    verdict: Verdict
    checks: tuple[RecordCheck, ...]
    first_bad: RecordCheck | None

    @property
    def ok(self) -> bool:
        return self.verdict is Verdict.VERIFIED_OK

    @property
    def banner(self) -> str:
        """The line a viewer paints, green or red."""
        if self.ok:
            return f"{Verdict.VERIFIED_OK.value} — {len(self.checks)} steps re-verified"
        bad = self.first_bad
        assert bad is not None  # a TAMPERED verdict always names its step
        return f"{Verdict.TAMPERED.value} — step {bad.step!r}: {bad.reason}"


def verify_record(record: Mapping[str, object], index: int = 0) -> RecordCheck:
    """Recompute one record's commitment from the file's own bytes.

    ``protocol.crypto.verify`` **raises** rather than returning a flag, so the translation
    to a verdict happens here: a record that cannot be checked is `TAMPERED`, not an
    exception. Damaging a record must not be an easier escape than rewriting one, and the
    reference collapses its own `CryptoError` to the same red banner.

    Refusing a log that was never revealed at all is a different matter and belongs to
    `load`, which separates a peer who has not yet revealed from one who has forged.
    """
    step = record.get("step") if isinstance(record, Mapping) else None
    if not isinstance(record, Mapping):
        return RecordCheck(index, step, Verdict.TAMPERED, "record is not an object")
    missing = [name for name in REVEAL_FIELDS if name not in record]
    if missing:
        return RecordCheck(
            index, step, Verdict.TAMPERED, f"record carries no {', '.join(missing)}"
        )
    try:
        verify(record["payload"], record["nonce"], record["commit"])  # type: ignore[arg-type]
    except (CryptoError, TypeError, AttributeError) as error:
        return RecordCheck(index, step, Verdict.TAMPERED, f"commitment rejected: {error}")
    disagreeing = _visible_fields_contradicting_the_seal(record)
    if disagreeing:
        return RecordCheck(
            index, step, Verdict.TAMPERED,
            f"visible {', '.join(disagreeing)} contradicts the sealed payload",
        )
    return RecordCheck(index, step, Verdict.VERIFIED_OK, "reveal matches commit")


def _visible_fields_contradicting_the_seal(record: Mapping[str, object]) -> list[str]:
    """Which displayed fields disagree with the payload the commitment actually covers.

    The commitment binds the *payload*; it says nothing about the record's own `step` and
    `move` keys, which are what a viewer paints on the board. Without this, a forger can
    leave the seal untouched, rewrite only the display, and collect a green stamp over a
    game nobody played.

    `:1691` closes it: the viewer re-encodes "the Nonce and the move **appearing in the
    log**", so the move appearing in the log must be the move that was sealed. Compared by
    key intersection, so a payload that later seals a position is covered without anyone
    remembering to extend a list.
    """
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        return []
    return sorted(
        name
        for name, sealed in payload.items()
        if name in record and name not in REVEAL_FIELDS and record[name] != sealed
    )


def verify_records(records: Sequence[Mapping[str, object]]) -> MatchVerdict:
    """Verify every record; the match is void on the first divergence.

    Every record is checked even after a failure, because "which step" is the auditor's
    next question and re-running to answer it would mean trusting the same code twice.
    """
    if not records:
        return MatchVerdict(
            Verdict.TAMPERED, (),
            RecordCheck(0, None, Verdict.TAMPERED, "log has no records to verify"),
        )
    checks = tuple(verify_record(record, index) for index, record in enumerate(records))
    first_bad = next((check for check in checks if not check.ok), None)
    return MatchVerdict(
        Verdict.VERIFIED_OK if first_bad is None else Verdict.TAMPERED, checks, first_bad
    )
