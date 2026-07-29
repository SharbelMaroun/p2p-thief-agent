"""Capability negotiation, heartbeat, abort, and closed-state evidence."""

from copy import deepcopy

import pytest

from p2p_thief_agent.protocol.profile import ConformanceError
from tests.contract.conformance_fixtures import (
    NONCE_1,
    NOW_MS,
    audit_record,
    make_audit,
    make_control,
    make_session,
    make_turn,
)


def test_unnegotiated_control_is_unavailable_without_mutation() -> None:
    session = make_session()

    with pytest.raises(ConformanceError) as captured:
        session.receive_control(make_control(), now_ms=NOW_MS)

    assert captured.value.code == "OPTIONAL_TOOL_UNAVAILABLE"
    assert session.next_step == 1


def test_heartbeat_is_state_preserving_and_idempotent() -> None:
    session = make_session(optional_control=True)
    message = make_control()

    first = session.receive_control(message, now_ms=NOW_MS)
    second = session.receive_control(deepcopy(message), now_ms=NOW_MS)

    assert first == second
    assert first["control"] == "heartbeat"
    assert session.next_step == 1


def test_abort_closes_stream_and_new_abort_is_replay() -> None:
    session = make_session(optional_control=True)
    abort = make_control("abort")
    acknowledgement = session.receive_control(abort, now_ms=NOW_MS)

    assert acknowledgement["control"] == "abort"
    assert session.receive_control(deepcopy(abort), now_ms=NOW_MS) == acknowledgement
    with pytest.raises(ConformanceError) as turn_error:
        session.receive_move(make_turn()[0], now_ms=NOW_MS)
    with pytest.raises(ConformanceError) as replay_error:
        session.receive_control(
            make_control("abort", message_id="d" * 32),
            now_ms=NOW_MS,
        )

    assert turn_error.value.code == "OUT_OF_ORDER"
    assert replay_error.value.code == "REPLAYED_MESSAGE"


def test_verified_audit_closes_turn_and_audit_streams() -> None:
    session = make_session()
    turn, payload, nonce = make_turn()
    session.receive_move(turn, now_ms=NOW_MS)
    audit = make_audit([audit_record(turn, payload, nonce)])
    session.submit_audit(audit, now_ms=NOW_MS)

    with pytest.raises(ConformanceError) as turn_error:
        session.receive_move(make_turn(2, nonce=NONCE_1)[0], now_ms=NOW_MS)
    with pytest.raises(ConformanceError) as audit_error:
        session.submit_audit(
            make_audit([], message_id="e" * 32),
            now_ms=NOW_MS,
        )

    assert turn_error.value.code == "OUT_OF_ORDER"
    assert audit_error.value.code == "REPLAYED_MESSAGE"


def test_control_schema_and_private_precedence_fail_closed() -> None:
    session = make_session(optional_control=True)
    invalid = make_control()
    invalid["body"]["extra"] = True
    leaking = make_control()
    leaking["payload"] = {}

    with pytest.raises(ConformanceError) as schema_error:
        session.receive_control(invalid, now_ms=NOW_MS)
    with pytest.raises(ConformanceError) as privacy_error:
        session.receive_control(leaking, now_ms=NOW_MS)

    assert schema_error.value.code == "UNKNOWN_FIELD"
    assert privacy_error.value.code == "PRIVATE_FIELD_LEAK"
