"""`M5-017`: two peers reach the same terminal outcome, or it is a visible conflict.

The result is not something either peer asserts on its own — it is *derived* from the
shared, audited transcript, so both sides compute it and must agree before any report.
Under `THIEF-002` there is no Cop repository to run, so the opponent's view is modelled
here by a neutral verifier that reasons **only** from the Thief's revealed audit: it
learns where the Thief actually stood each step and checks its own capture claim against
that reveal. That is exactly what the real mutual audit does — each peer recomputes the
other's record — so agreement proven this way is agreement the audit enforces.

The third case is the point of commit-reveal: a Thief that *denies* a correct capture
keeps playing on the wire, but its own sealed positions expose the lie, so the two peers
diverge and that divergence is a conflict scored 0/0, never a quiet Thief win
`[AE-19]` `[AE-21]`.
"""

from p2p_thief_agent.state.scoring import Outcome, wire_result_claim
from tests.unit.test_sub_game import Opponent, cop_turn, play


def revealed_position(audit: dict, step: int) -> list | None:
    """Where the Thief's own reveal says it stood at ``step`` (None if never sealed)."""
    for record in audit["records"]:
        if record["payload"]["step"] == step:
            return record["payload"]["position"]
    return None


def opponent_result_claim(audit: dict, *, capture_claim: list | None, adjudicated_at: int) -> str:
    """The opponent's view, computed only from the Thief's reveal — no shared memory.

    A claim confirmed by the Thief's own sealed position is a capture; anything else is
    the Thief having survived the exchange.
    """
    if capture_claim is not None and revealed_position(audit, adjudicated_at) == capture_claim:
        return "capture"
    return "survival"


def test_a_capture_is_reached_by_both_sides() -> None:
    """`decide` seals position `[3, step]`, so the Cop's claim `[3, 3]` is the Thief's
    real step-3 cell — its own audit confirms it, and both sides read `capture`."""
    thief = play(
        Opponent(cop_turn(1), cop_turn(2, capture_claim=[3, 3]), cop_turn(3)),
        answer=lambda cell: cell == [3, 3],
    )
    assert thief.outcome is Outcome.CAPTURE
    theirs = opponent_result_claim(thief.audit, capture_claim=[3, 3], adjudicated_at=3)
    assert wire_result_claim(thief.outcome) == theirs == "capture"


def test_a_survival_is_reached_by_both_sides() -> None:
    """No claim ever lands, so the transcript carries no capture and both read `survival`."""
    thief = play(Opponent(*(cop_turn(s) for s in range(1, 5))), threshold=5)
    assert thief.outcome is Outcome.SURVIVAL
    theirs = opponent_result_claim(thief.audit, capture_claim=None, adjudicated_at=0)
    assert wire_result_claim(thief.outcome) == theirs == "survival"


def test_a_denied_but_true_capture_is_a_visible_conflict_not_a_thief_win() -> None:
    """The Thief answers `False` to a claim its own reveal proves correct.

    On the wire it plays on and calls the result `survival`; the opponent, recomputing
    from the Thief's sealed `[3, 3]` at step 3, calls it `capture`. The two disagree —
    a conflict, which rule 19 scores 0/0 — so lying cannot buy a quiet win.
    """
    thief = play(
        Opponent(cop_turn(1), cop_turn(2, capture_claim=[3, 3]), cop_turn(3), cop_turn(4)),
        threshold=5,
        answer=lambda _cell: False,
    )
    assert thief.outcome is Outcome.SURVIVAL
    mine = wire_result_claim(thief.outcome)
    theirs = opponent_result_claim(thief.audit, capture_claim=[3, 3], adjudicated_at=3)
    assert mine == "survival" and theirs == "capture"
    assert mine != theirs  # a conflict the audit makes visible, never a silent divergence
