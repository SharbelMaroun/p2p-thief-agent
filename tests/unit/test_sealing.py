"""Unit tests for the simulator-conformant sealing helpers."""

from p2p_thief_agent.protocol.crypto import verify
from p2p_thief_agent.protocol.sealing import (
    StepDecision,
    build_turn_message,
    sealed_spec_record,
    sealed_step_payload,
    sealed_step_record,
    state_str,
)


def decision() -> StepDecision:
    return StepDecision(move="N", verdict="lie", hint="Central Park", response_seconds=0.5)


def test_state_str_format_and_barrier_ordering():
    text = state_str(7, [3, 3], [[4, 4], [2, 2]])
    assert text == "grid=7x7;self=[3, 3];barriers=[[2, 2], [4, 4]]"


def test_sealed_step_payload_has_full_roster():
    payload = sealed_step_payload(
        step=1, board_size=7, position=[3, 3], barriers=[], decision=decision()
    )
    assert payload["move"] == "N"
    assert payload["intent"] == payload["verdict"] == "lie"
    assert payload["hint"] == "Central Park"
    assert payload["prompt_discussion"]["bluff_classification"] == "lie"
    assert payload["state"] == "grid=7x7;self=[3, 3];barriers=[]"
    assert set(payload) >= {
        "step", "state", "position", "move", "intent", "verdict", "hint",
        "prompt_discussion", "model", "tokens_step", "tokens_total",
        "response_seconds", "random_move",
    }


def test_sealed_step_record_commits_and_verifies():
    record = sealed_step_record(
        step=1, board_size=7, position=[3, 3], barriers=[], decision=decision()
    )
    verify(record["payload"], record["nonce"], record["commit"])


def test_sealed_spec_record_is_step_zero():
    record = sealed_spec_record(spec={"cpu": "x"}, model="cli-default", group_name="sharNamr")
    assert record["payload"]["step"] == 0
    assert record["payload"]["type"] == "system_spec"
    assert record["payload"]["group_name"] == "sharNamr"
    verify(record["payload"], record["nonce"], record["commit"])


def test_build_turn_message_carries_commit_and_timestamp():
    message = build_turn_message(
        step=1, sender="thief", hint="hi", smell_grid={}, commit="a" * 64,
        barrier_placed=[2, 2],
    )
    assert message.sender == "thief"
    assert message.commit == "a" * 64
    assert message.barrier_placed == [2, 2]
    assert message.timestamp  # non-empty ISO string
