"""Unit tests for the simulator-conformant envelope-free wire messages."""

import pytest

from p2p_thief_agent.protocol.wire import (
    AuditPayload,
    ControlMessage,
    TurnMessage,
    WireError,
)


def turn_dict() -> dict:
    return {
        "step": 1,
        "sender": "thief",
        "hint": "Central Park",
        "smell_grid": {"3,3": 0.9},
        "commit": "a" * 64,
        "timestamp": "2026-07-29T00:00:00+00:00",
        "barrier_placed": None,
        "capture_claim": None,
        "claim_response": None,
        "win_claim": None,
    }


def test_turn_round_trip():
    message = TurnMessage.from_dict(turn_dict())
    assert message.step == 1 and message.sender == "thief"
    assert message.to_dict() == turn_dict()


def test_turn_requires_core_fields():
    incomplete = turn_dict()
    del incomplete["commit"]
    with pytest.raises(WireError, match="missing fields"):
        TurnMessage.from_dict(incomplete)


def test_turn_rejects_unknown_field():
    extended = turn_dict()
    extended["position"] = [3, 3]
    with pytest.raises(WireError, match="unknown fields"):
        TurnMessage.from_dict(extended)


def test_turn_rejects_bad_sender():
    bad = turn_dict()
    bad["sender"] = "cop"
    with pytest.raises(WireError, match="sender"):
        TurnMessage.from_dict(bad)


def test_turn_optional_fields_default_null():
    minimal = {
        "step": 2,
        "sender": "police",
        "hint": "hi",
        "smell_grid": {},
        "commit": "b" * 64,
        "timestamp": "t",
    }
    message = TurnMessage.from_dict(minimal)
    assert message.barrier_placed is None
    assert message.capture_claim is None
    assert message.win_claim is None


def test_turn_message_must_be_object():
    with pytest.raises(WireError, match="must be an object"):
        TurnMessage.from_dict(["not", "a", "dict"])


def test_control_ignores_unknown_keys():
    message = ControlMessage.from_dict(
        {"kind": "status", "sender": "thief", "status": "PLAYING", "extra": "ignored"}
    )
    assert message.kind == "status"
    assert message.status == "PLAYING"
    assert not hasattr(message, "extra")


def test_control_message_must_be_object():
    with pytest.raises(WireError, match="must be an object"):
        ControlMessage.from_dict("nope")


def test_control_requires_kind_and_sender():
    with pytest.raises(WireError, match="missing fields"):
        ControlMessage.from_dict({"kind": "quit"})


def test_control_defaults():
    message = ControlMessage.from_dict({"kind": "enable", "sender": "police"})
    assert message.sub_game_number == 1
    assert message.step_budget == 0.0
    assert message.payload is None
    assert message.to_dict()["kind"] == "enable"


def test_audit_round_trip_and_claim_validation():
    records = [{"payload": {"step": 1}, "nonce": "0" * 32, "commit": "a" * 64}]
    audit = AuditPayload.from_dict(
        {"sender": "thief", "records": records, "result_claim": "survival"}
    )
    assert audit.result_claim == "survival"
    assert audit.to_dict()["records"] == records


def test_control_rejects_bad_sender():
    with pytest.raises(WireError, match="sender"):
        ControlMessage.from_dict({"kind": "status", "sender": "referee"})


def test_audit_rejects_bad_sender_and_nonlist_records():
    with pytest.raises(WireError, match="sender"):
        AuditPayload.from_dict({"sender": "x", "records": [], "result_claim": "capture"})
    with pytest.raises(WireError, match="records"):
        AuditPayload.from_dict({"sender": "thief", "records": {}, "result_claim": "capture"})


def test_audit_rejects_bad_result_claim():
    with pytest.raises(WireError, match="result_claim"):
        AuditPayload.from_dict({"sender": "thief", "records": [], "result_claim": "tie"})


def test_audit_rejects_unknown_field():
    with pytest.raises(WireError, match="unknown fields"):
        AuditPayload.from_dict(
            {"sender": "thief", "records": [], "result_claim": "capture", "x": 1}
        )
