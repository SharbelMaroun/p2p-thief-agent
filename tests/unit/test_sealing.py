"""Unit tests for the simulator-conformant sealing helpers."""

import pytest

from p2p_thief_agent.protocol.crypto import verify
from p2p_thief_agent.protocol.sealing import (
    SealingError,
    StepDecision,
    build_turn_message,
    sealed_spec_record,
    sealed_step_payload,
    sealed_step_record,
    state_str,
)

COMMIT = "0123456789abcdef0123456789abcdef01234567"


def spec_record(**overrides) -> dict:
    kwargs = {
        "spec": {"cpu": "x"}, "model": "cli-default", "group_name": "sharNamr",
        "github_commit": COMMIT, "token_budget": 100000,
    }
    kwargs.update(overrides)
    return sealed_spec_record(**kwargs)


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
    record = spec_record()
    assert record["payload"]["step"] == 0
    assert record["payload"]["type"] == "system_spec"
    assert record["payload"]["group_name"] == "sharNamr"
    verify(record["payload"], record["nonce"], record["commit"])


def test_sealed_spec_record_binds_the_git_commit_and_token_budget():
    """`M4-006a`/`M4-006b`: the running commit (AE-53) and token budget (AE-54) are sealed."""
    payload = spec_record()["payload"]
    assert payload["github_commit"] == COMMIT
    assert payload["token_budget"] == 100000


def test_sealed_spec_record_refuses_a_missing_commit():
    with pytest.raises(SealingError, match="github_commit is required"):
        spec_record(github_commit="")


@pytest.mark.parametrize("bad", [-1, True, "100", 1.5])
def test_sealed_spec_record_refuses_a_nonsensical_token_budget(bad):
    with pytest.raises(SealingError, match="token_budget must be a non-negative integer"):
        spec_record(token_budget=bad)


def test_build_turn_message_carries_commit_and_timestamp():
    message = build_turn_message(
        step=1, sender="thief", hint="hi", smell_grid={}, commit="a" * 64,
        barrier_placed=[2, 2],
    )
    assert message.sender == "thief"
    assert message.commit == "a" * 64
    assert message.barrier_placed == [2, 2]
    assert message.timestamp  # non-empty ISO string
