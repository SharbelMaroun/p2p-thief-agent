"""`M5-007`: the audit that makes a Thief's answers binding.

A capture claim is answered from local truth, and nothing on the wire forces that
answer to be honest. The audit is what does: every sealed record carries this peer's
true position, so a false denial is contradicted by its own reveal — and a forgery
scores zero for both sides while an honest loss still scores `[AE-019]`.

The sub-game's decision logic lives in `test_sub_game.py`.
"""

import pytest

from p2p_thief_agent.orchestration.turn_loop import TurnLoopError
from p2p_thief_agent.protocol.crypto import audit_records
from p2p_thief_agent.state.scoring import Outcome
from tests.unit.test_sub_game import Opponent, cop_turn, play
from tests.unit.test_turn_loop import Sink


def test_the_audit_reveals_every_sealed_turn_and_recomputes() -> None:
    result = play(Opponent(*(cop_turn(s) for s in range(1, 3))), threshold=3)

    assert result.audit is not None
    assert result.audit["sender"] == "thief"
    assert len(result.audit["records"]) == 3
    assert audit_records(result.audit["records"])["passed"] is True


def test_the_sealed_records_carry_the_true_position_each_step() -> None:
    """This is why a false denial cannot pay: our own reveal contradicts it."""
    result = play(Opponent(*(cop_turn(s) for s in range(1, 3))), threshold=3)
    positions = [record["payload"]["position"] for record in result.audit["records"]]
    assert positions == [[3, 1], [3, 2], [3, 3]]


def test_the_audit_claim_matches_the_outcome() -> None:
    survived = play(Opponent(*(cop_turn(s) for s in range(1, 3))), threshold=3)
    assert survived.audit["result_claim"] == "survival"

    caught = play(Opponent(cop_turn(1, capture_claim=[3, 1])), answer=lambda _c: True)
    assert caught.audit["result_claim"] == "capture"


def test_the_audit_is_delivered_to_the_opponent() -> None:
    class Recorder(Sink):
        def __init__(self) -> None:
            super().__init__()
            self.audits: list[dict] = []

        def submit_audit(self, payload: dict) -> dict:
            self.audits.append(payload)
            return {"ok": True}

    peer = Recorder()
    play(Opponent(cop_turn(1)), threshold=2, transport=peer)
    assert len(peer.audits) == 1
    assert audit_records(peer.audits[0]["records"])["passed"] is True


def test_a_technical_loss_still_sends_its_audit() -> None:
    """A withheld reveal cannot be checked, which helps nobody."""
    result = play(Opponent(), threshold=3)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.audit["result_claim"] == "timeout"


def test_an_opponent_that_has_left_does_not_break_the_reveal() -> None:
    class Gone(Sink):
        def submit_audit(self, payload: dict) -> dict:
            raise ConnectionError("peer already exited")

    result = play(Opponent(cop_turn(1)), threshold=2, transport=Gone())
    assert audit_records(result.audit["records"])["passed"] is True


@pytest.mark.parametrize("bad", [0, -1, True, "35", None])
def test_an_invalid_threshold_is_refused(bad: object) -> None:
    with pytest.raises(TurnLoopError, match="survival_threshold"):
        play(Opponent(cop_turn(1)), threshold=bad)
