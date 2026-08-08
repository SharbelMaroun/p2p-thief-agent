"""Audit the series, then agree the result — in that order (`M7-016`).

Rule 36 (Mandatory) does not merely require an audit; it fixes its **position**: "Perform
a comprehensive mutual audit log at the end of every game. Sanction: **Mandatory condition
before agreement on the JSON result**." So `agree` takes a passed audit as its first
argument and there is no path to agreement without one — a precondition a caller can
forget is not a precondition.

**Two sanctions, two different victims, and conflating them is expensive.**

* **Rule 19** — "Reject any game technical mismatch during the audit phase. Sanction: Iron
  rule; score of 0 for **the falsifying group**." One side, the guilty one.
* **Rule 35** — "a conflicting report causes disqualification of the game and a score of 0
  for **both teams**."

Catching an opponent's forgery is therefore not a reason to fire off our own contradicting
report: that converts *their* rule 19 loss into a rule 35 loss we share. A failed audit
means we do not agree and do not report; it does not mean we race them to the lecturer.

**A disagreement is recorded, never smoothed over.** Adopting their number to keep the
peace files a result we do not believe and destroys the evidence an auditor needs. Both
claims stay visible.

*Built on this repository's own `protocol.crypto.audit_records`.* The companion Cop repo
solved the same problem today, but `THIEF-002` forbids reading it and `M1-015` set the
discipline: the design travels, the bytes do not.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from p2p_thief_agent.protocol.crypto import audit_records


class Settled(StrEnum):
    """How a series ended. Only `AGREED` may be reported."""

    AGREED = "agreed"
    CONFLICT = "conflict"            # rule 35: 0/0 for both
    AUDIT_FAILED = "audit_failed"    # rule 19: 0 for the falsifying group
    UNANSWERED = "unanswered"        # the peer never replied


class SettlementError(RuntimeError):
    """Raised when a caller tries to agree or report out of order."""


@dataclass(frozen=True, slots=True)
class SeriesAudit:
    """The audit across every sub-game. `passed` is the only gate to agreement."""

    passed: bool
    sub_games: tuple[int, ...]
    failed_at: int | None
    failed_steps: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class Settlement:
    """The outcome of settling, with both sides' claims kept side by side."""

    state: Settled
    ours: object
    theirs: object = None
    audit: SeriesAudit | None = None

    @property
    def reportable(self) -> bool:
        return self.state is Settled.AGREED


def audit_series(reveals: Sequence[Mapping[str, object]]) -> SeriesAudit:
    """Re-verify every sub-game's revealed records, stopping at the first failure.

    Rule 19 calls a mismatch an "iron rule", so there is nothing to weigh once one is
    found; continuing would only obscure which sub-game broke.
    """
    if not reveals:
        return SeriesAudit(False, (), None)
    numbers: list[int] = []
    for reveal in reveals:
        number = reveal.get("sub_game")
        numbers.append(number if isinstance(number, int) else -1)
        records = reveal.get("records")
        if not isinstance(records, list) or not records:
            return SeriesAudit(False, tuple(numbers), numbers[-1])
        summary = audit_records(records)
        if not summary["passed"]:
            return SeriesAudit(False, tuple(numbers), numbers[-1],
                               tuple(summary.get("failed_steps") or ()))
    return SeriesAudit(True, tuple(numbers), None)


def agree(audit: SeriesAudit, ours: object, theirs: object) -> Settlement:
    """Compare the two computed outcomes — but only after a passed audit."""
    if not audit.passed:
        return Settlement(Settled.AUDIT_FAILED, ours, theirs, audit)
    if theirs is None:
        return Settlement(Settled.UNANSWERED, ours, None, audit)
    if ours != theirs:
        return Settlement(Settled.CONFLICT, ours, theirs, audit)
    return Settlement(Settled.AGREED, ours, theirs, audit)


def require_reportable(settlement: Settlement) -> None:
    """Refuse to report anything but an agreed result.

    Each state gets its own message because they call for different actions: a conflict
    needs a human and the lecturer, an audit failure needs the evidence preserved, and
    silence needs a retry of the *exchange* rather than of the report.
    """
    if settlement.reportable:
        return
    reasons = {
        Settled.CONFLICT: (
            f"the two sides disagree ({settlement.ours!r} vs {settlement.theirs!r}); rule 35 "
            "scores a conflicting report 0 for BOTH teams, so this must not be sent"
        ),
        Settled.AUDIT_FAILED: (
            "the mutual audit did not pass, and rule 36 makes it a mandatory condition "
            "before agreement; reporting now would turn their rule 19 loss into a shared one"
        ),
        Settled.UNANSWERED: "the opponent never returned an outcome; nothing is agreed to report",
    }
    raise SettlementError(reasons[settlement.state])


def settlement_record(settlement: Settlement) -> Mapping[str, object]:
    """The `mutual_agreement` block for the log artifact — both claims, kept visible."""
    return {
        "state": settlement.state.value,
        "our_outcome": settlement.ours,
        "their_outcome": settlement.theirs,
        "audit_passed": bool(settlement.audit and settlement.audit.passed),
        "audit_failed_at": settlement.audit.failed_at if settlement.audit else None,
    }
