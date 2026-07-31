"""`M5-007`: one turn, driven by the phase machine, over a fake transport.

No socket here on purpose — the loop is transport-neutral, so a turn can be driven,
starved, and broken deterministically. The wire itself is proven in
`tests/integration/`.
"""

import pytest

from p2p_thief_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_thief_agent.orchestration.phases import Phase, PhaseMachine
from p2p_thief_agent.orchestration.turn_loop import (
    TurnLoopError,
    is_sealed_once,
    run_turn,
    sealed_steps,
)
from p2p_thief_agent.protocol.crypto import seal
from p2p_thief_agent.protocol.wire import WireError

COP_TURN = {"step": 1, "sender": "police", "hint": "near the bridge",
            "smell_grid": {"0,0": 0.9}, "commit": "a" * 64, "timestamp": "t1"}


class Sink:
    """A transport that records what it was sent and answers however it is told."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.sent: list[dict] = []

    def receive_turn(self, message: dict) -> dict:
        self.sent.append(message)
        if self.error is not None:
            raise self.error
        return {"ok": True}


def decide(_incoming: dict | None, step: int) -> tuple[dict, dict]:
    """Return the public turn and the private sealed record for one step."""
    payload = {"step": step, "state": f"grid=7x7;self=[3, {step}];barriers=[]",
               "position": [3, step], "move": "MOVE:S", "verdict": "truth",
               "hint": "still running"}
    sealed = seal(payload)
    message = {"step": step, "sender": "thief", "hint": payload["hint"],
               "smell_grid": {"3,3": 0.9}, "commit": sealed["commit"],
               "timestamp": f"t{step}"}
    return message, {"payload": payload, **sealed}


def test_one_turn_walks_the_declared_phases_in_order() -> None:
    machine, records = PhaseMachine(), []
    record = run_turn(1, machine=machine, transport=Sink(), receive=lambda: COP_TURN,
                      decide=decide, records=records)

    assert record.phases == (
        Phase.COMPUTING_MOVE, Phase.COMMITTING, Phase.AWAITING_REVEAL,
        Phase.VERIFYING, Phase.WAITING_FOR_OPPONENT,
    )
    assert machine.current is Phase.WAITING_FOR_OPPONENT


def test_the_turn_sent_carries_the_commit_and_never_the_move() -> None:
    """The move stays private until the audit — the wire carries only a hash."""
    sink, records = Sink(), []
    run_turn(1, machine=PhaseMachine(), transport=sink, receive=lambda: COP_TURN,
             decide=decide, records=records)

    sent = sink.sent[0]
    assert set(sent) >= {"step", "sender", "hint", "smell_grid", "commit", "timestamp"}
    assert "move" not in sent and "position" not in sent and "verdict" not in sent
    assert "nonce" not in sent and len(sent["commit"]) == 64


def test_the_thief_opens_without_waiting() -> None:
    """The book gives the Thief the first move, so step 1 awaits nothing.

    A Thief that waited here would deadlock against a Cop correctly waiting for it.
    """
    def starve() -> dict | None:
        raise AssertionError("an opening turn must not await the opponent")

    record = run_turn(1, machine=PhaseMachine(), transport=Sink(), receive=starve,
                      decide=decide, records=[], opens=True)
    assert record.received is None


def test_a_following_turn_receives_before_it_computes() -> None:
    record = run_turn(2, machine=PhaseMachine(), transport=Sink(), receive=lambda: COP_TURN,
                      decide=decide, records=[])
    assert record.received == COP_TURN


def test_every_transition_is_reported_for_the_log() -> None:
    seen: list[Phase] = []
    run_turn(1, machine=PhaseMachine(), transport=Sink(), receive=lambda: COP_TURN,
             decide=decide, records=[], on_transition=seen.append)
    assert seen == [
        Phase.COMPUTING_MOVE, Phase.COMMITTING, Phase.AWAITING_REVEAL,
        Phase.VERIFYING, Phase.WAITING_FOR_OPPONENT,
    ]


def test_each_step_is_sealed_exactly_once() -> None:
    machine, records, sink = PhaseMachine(), [], Sink()
    for step in (1, 2, 3):
        run_turn(step, machine=machine, transport=sink, receive=lambda: COP_TURN,
                 decide=decide, records=records)

    assert sealed_steps(records) == (1, 2, 3)
    assert all(is_sealed_once(records, step) for step in (1, 2, 3))


def test_a_silent_opponent_reaches_the_terminal_state_rather_than_hanging() -> None:
    """`AE-007`: silence is not patience; it must decide, not wait forever."""
    machine = PhaseMachine()
    with pytest.raises(TurnLoopError, match="did not send a turn"):
        run_turn(2, machine=machine, transport=Sink(), receive=lambda: None,
                 decide=decide, records=[])
    assert machine.current is Phase.TECHNICAL_LOSS
    assert machine.history[-2:] == (Phase.COMPUTING_MOVE, Phase.TECHNICAL_LOSS)


@pytest.mark.parametrize("failure", [TransportError("unreachable"), PeerRejectionError("no")])
def test_a_turn_sealed_but_undelivered_is_never_resealed(failure: Exception) -> None:
    """Re-sealing would give one step two hashes and fail the audit `[AE-019]`."""
    machine, records = PhaseMachine(), []
    with pytest.raises(TurnLoopError, match="sealed but not delivered"):
        run_turn(1, machine=machine, transport=Sink(error=failure), receive=lambda: COP_TURN,
                 decide=decide, records=records, opens=True)

    assert is_sealed_once(records, 1)
    assert machine.current is Phase.TECHNICAL_LOSS


def test_a_decision_that_cannot_be_sealed_ends_the_turn() -> None:
    def broken(_incoming: dict | None, _step: int) -> tuple[dict, dict]:
        raise WireError("hint exceeds the agreed word limit")

    machine = PhaseMachine()
    with pytest.raises(TurnLoopError, match="could not be sealed"):
        run_turn(1, machine=machine, transport=Sink(), receive=lambda: COP_TURN,
                 decide=broken, records=[], opens=True)
    assert machine.current is Phase.TECHNICAL_LOSS


def test_a_transport_without_the_tool_is_refused() -> None:
    with pytest.raises(TurnLoopError, match="does not expose receive_turn"):
        run_turn(1, machine=PhaseMachine(), transport=object(), receive=lambda: COP_TURN,
                 decide=decide, records=[], opens=True)
