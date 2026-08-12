"""One whole sub-game over the wire, then the audit that settles it (`M5-007`).

The Thief's side of termination is **not** the mirror of the Cop's, and the
difference is the interesting part.

The Cop can only *claim* a capture: it names a cell and waits, because it cannot see
where the Thief stands. The Thief is the peer that **knows**. So when a
``capture_claim`` arrives, this peer does not wait for anyone to adjudicate — it
answers from its own local truth, and if the claim is correct the sub-game is over.

That asymmetry is also where the duty of truth bites. The Thief could answer
``caught: false`` to a correct claim and play on, and nothing on the wire would stop
it. What stops it is the audit: its own sealed records carry its true position each
step, so a false denial is exposed by arithmetic when every commitment is recomputed,
and a forgery scores **zero for both sides** while an honest loss still scores
`[AE-019]` `[AE-021]` `[AE-022]`. Lying is strictly worse than losing.

Survival is this peer's to declare: on outlasting the agreed threshold it says so in
``win_claim``. The horizon is **inclusive** — completing the final step uncaught is a
win, not one step short of one (`U-022`).
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass

from p2p_thief_agent.orchestration.phases import PhaseMachine
from p2p_thief_agent.orchestration.turn_loop import (
    Decide,
    Deliver,
    OnTransition,
    Receive,
    TurnLoopError,
    TurnRecord,
    run_turn,
)
from p2p_thief_agent.state.scoring import Outcome, wire_result_claim

# Given a claimed cell, report whether this peer actually stood there. Supplied by
# the caller from Thief-local state, so this module holds no position of its own.
AnswerClaim = Callable[[list], bool]


@dataclass(frozen=True, slots=True)
class SubGameOutcome:
    """How one sub-game ended, and the audit this peer revealed to prove its play."""

    outcome: Outcome
    steps: int
    reason: str
    turns: tuple[TurnRecord, ...]
    audit: dict | None = None


def run_sub_game_over_wire(
    *,
    machine: PhaseMachine,
    transport: object,
    receive: Receive,
    decide: Decide,
    answer_claim: AnswerClaim,
    survival_threshold: int,
    records: list[dict] | None = None,
    on_transition: OnTransition | None = None,
    send_audit: bool = True,
    deliver: Deliver | None = None,
    step_zero: dict | None = None,
) -> SubGameOutcome:
    """Play turns until decided, then reveal every sealed record.

    This peer **opens**: the book gives the Thief the first move of every turn cycle,
    so step 1 does not wait for the opponent. A Thief that waited would deadlock
    against a Cop correctly waiting for it.

    ``deliver`` is passed straight to `run_turn`; over a real tunnel it should carry the
    agreed bounded retry, or one transient fault ends the sub-game (see `_deliver`).
    """
    if isinstance(survival_threshold, bool) or not isinstance(survival_threshold, int):
        raise TurnLoopError(f"survival_threshold must be an integer, got {survival_threshold!r}")
    if survival_threshold < 1:
        raise TurnLoopError(f"survival_threshold must be positive, got {survival_threshold}")

    ledger: list[dict] = records if records is not None else []
    turns: list[TurnRecord] = []

    for step in range(1, survival_threshold + 1):
        try:
            record = run_turn(
                step,
                machine=machine,
                transport=transport,
                receive=receive,
                decide=decide,
                records=ledger,
                opens=step == 1,
                on_transition=on_transition,
                deliver=deliver,
            )
        except TurnLoopError as exc:
            return _finish(Outcome.TECHNICAL_LOSS, step - 1, str(exc), turns, ledger,
                           transport, send_audit, step_zero)
        turns.append(record)

        caught = _caught_by(record.received, answer_claim)
        if caught is not None:
            return _finish(Outcome.CAPTURE, step, caught, turns, ledger, transport,
                           send_audit, step_zero)

    return _finish(
        Outcome.SURVIVAL,
        survival_threshold,
        f"survived the agreed limit of {survival_threshold} steps",
        turns, ledger, transport, send_audit, step_zero,
    )


def _caught_by(message: dict | None, answer_claim: AnswerClaim) -> str | None:
    """Return why this peer was captured, or None if it was not.

    A claim is only ever *checked*, never believed. An incorrect claim is simply the
    game continuing — answering it truthfully is what the audit later verifies.
    """
    if not isinstance(message, dict):
        return None
    claim = message.get("capture_claim")
    if claim is None:
        return None
    if answer_claim(claim):
        return f"the opponent's capture claim at {claim!r} was correct"
    return None


def _finish(
    outcome: Outcome,
    steps: int,
    reason: str,
    turns: list[TurnRecord],
    records: list[dict],
    transport: object,
    send_audit: bool,
    step_zero: dict | None = None,
) -> SubGameOutcome:
    """Reveal every sealed record, then report the outcome.

    The audit goes out even when this peer is taking the technical loss: a reveal
    that is withheld cannot be checked, and the whole point is that the opponent
    recomputes it.

    ``step_zero`` is the sealed `system_spec` attestation (rule 24). It is prepended to
    the **audit** records but never to the ledger the log is written from -- the reference
    convention, confirmed with uoh-ay26 on 2026-08-12: the audit carries a step-0
    `system_spec` record that peers unconditionally expect, while the saved game log
    excludes it. We build the record (`sealed_spec_record`) but had never attached it to
    the audit, so every cross-team audit was rejected "at steps [0]".
    """
    audit: dict | None = None
    if send_audit:
        audit_records = [step_zero, *records] if step_zero is not None else list(records)
        audit = {
            "sender": "thief",
            "records": audit_records,
            "result_claim": wire_result_claim(outcome),
        }
        submit = getattr(transport, "submit_audit", None)
        if submit is not None:
            # A peer that has already left cannot receive its proof; the reveal is
            # still built and returned, so this side's record stands either way.
            with suppress(Exception):
                submit(audit)
    return SubGameOutcome(outcome, steps, reason, tuple(turns), audit)
