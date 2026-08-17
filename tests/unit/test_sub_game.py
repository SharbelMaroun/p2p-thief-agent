"""`M5-007`: a whole sub-game, decided by this peer's own knowledge, then proven.

The asymmetry under test: the Cop can only *claim* a capture, while the Thief is the
peer that **knows**. So a claim here is checked against local truth, never believed —
and the audit is what later makes a false denial impossible to profit from.
"""


from p2p_thief_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_thief_agent.orchestration.phases import PhaseMachine
from p2p_thief_agent.orchestration.sub_game import run_sub_game_over_wire
from p2p_thief_agent.state.scoring import Outcome
from tests.unit.test_turn_loop import Sink, decide


def cop_turn(step: int, **extra: object) -> dict:
    return {"step": step, "sender": "police", "hint": "closing in",
            "smell_grid": {"0,0": 0.9}, "commit": "a" * 64,
            "timestamp": f"t{step}", **extra}


class Opponent:
    """Replays a scripted sequence of Cop turns, then falls silent."""

    def __init__(self, *messages: dict) -> None:
        self.messages = list(messages)

    def __call__(self) -> dict | None:
        return self.messages.pop(0) if self.messages else None


def play(receive, *, threshold: int = 5, transport=None, answer=lambda _cell: False, **kw):
    return run_sub_game_over_wire(
        machine=PhaseMachine(),
        transport=transport if transport is not None else Sink(),
        receive=receive,
        decide=decide,
        answer_claim=answer,
        survival_threshold=threshold,
        **kw,
    )


def test_surviving_the_threshold_wins_inclusively() -> None:
    """`U-022`: completing the final step uncaught is a win, not one short."""
    result = play(Opponent(*(cop_turn(s) for s in range(1, 5))), threshold=5)
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 5
    assert "survived the agreed limit" in result.reason


def test_a_correct_capture_claim_ends_the_sub_game() -> None:
    """Only this peer knows it was there, so it is this peer that concedes.

    **The settled step is the COP's, not ours** (`yanell11`, 2026-08-17). This asserted 3
    until then, and the old docstring explained why in the very words that show it was
    wrong: "step 1 opens without waiting, so the opponent's messages land one turn later
    than their own numbering suggests." That offset is not a quirk to document -- it is the
    28-against-29 our two teams' reports disagreed on for three series.

    A capture is caused by the Cop, so it settles in the Cop's numbering. The claim here
    rides the Cop's message numbered **2**, which this peer reads on its own step 3, so the
    answer is 2. Both sides now read the same integer off the same bytes instead of each
    reporting its own counter.
    """
    result = play(
        Opponent(cop_turn(1), cop_turn(2, capture_claim=[3, 2]), cop_turn(3)),
        answer=lambda cell: cell == [3, 2],
    )
    assert result.outcome is Outcome.CAPTURE
    assert result.steps == 2, "a capture settles on the Cop's turn, not on our concession"
    assert "capture claim at [3, 2] was correct" in result.reason


def test_an_incorrect_capture_claim_is_simply_the_game_continuing() -> None:
    """A claim is checked, never believed — a wrong one changes nothing."""
    result = play(
        Opponent(*(cop_turn(s, capture_claim=[0, 0]) for s in range(1, 5))),
        threshold=5,
        answer=lambda cell: cell == [3, 3],
    )
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 5


def test_a_turn_without_a_claim_is_never_treated_as_one() -> None:
    result = play(Opponent(*(cop_turn(s) for s in range(1, 3))), threshold=3,
                  answer=lambda _cell: True)
    assert result.outcome is Outcome.SURVIVAL


def test_a_silent_opponent_is_a_technical_loss_not_a_hang() -> None:
    """Two turns complete (the opener, then one reply) before the silence bites."""
    result = play(Opponent(cop_turn(1)), threshold=5)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.steps == 2
    assert "did not send a turn" in result.reason


def test_the_thief_opens_so_a_one_step_game_needs_no_incoming_turn() -> None:
    result = play(Opponent(), threshold=1)
    assert result.outcome is Outcome.SURVIVAL
    assert result.steps == 1


def test_a_mid_turn_disconnect_terminates_and_still_reveals_the_proof() -> None:
    """`M5-004e`: a dropped send from AWAITING_REVEAL ends the sub-game, never hangs.

    The opener seals its step, the delivery fails on a dropped tunnel, and the sub-game
    reaches a terminal technical loss rather than blocking. The audit is still built and
    returned, so this side's one sealed record stands even though the peer went away.
    """
    result = play(Opponent(), transport=Sink(error=TransportError("tunnel dropped")))
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.steps == 0
    assert "sealed but not delivered" in result.reason
    assert result.audit is not None and len(result.audit["records"]) == 1


def test_an_opponent_rejection_terminates_the_sub_game() -> None:
    """`M5-010b`: a content rejection reaches a defined terminal state, never a hang."""
    result = play(Opponent(), transport=Sink(error=PeerRejectionError("declined")))
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.steps == 0
    assert "sealed but not delivered" in result.reason
