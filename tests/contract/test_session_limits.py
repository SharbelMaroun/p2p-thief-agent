"""Wire limits, expiry boundaries, and cached-rejection conformance."""

from copy import deepcopy

import pytest

from p2p_thief_agent.protocol.profile import ConformanceError
from p2p_thief_agent.protocol.session import ConformanceSession
from tests.contract.conformance_fixtures import make_control, make_session, make_turn


def test_expiry_boundary_is_inclusive() -> None:
    session = make_session()
    message, _, _ = make_turn()

    acknowledgement = session.receive_turn(message, now_ms=message["expires_at_ms"])

    assert acknowledgement["status"] == "locked"


def test_turn_canonical_byte_limit_precedes_hint_limit() -> None:
    session = make_session()
    message, _, _ = make_turn()
    message["body"]["hint"] = "😀" * 4096

    with pytest.raises(ConformanceError) as captured:
        session.receive_turn(message, now_ms=150)

    assert captured.value.code == "MALFORMED"


def test_turn_depth_limit_is_enforced_before_schema() -> None:
    session = make_session()
    message, _, _ = make_turn()
    nested: object = None
    for _ in range(65):
        nested = [nested]
    message["body"] = nested

    with pytest.raises(ConformanceError) as captured:
        session.receive_turn(message, now_ms=150)

    assert captured.value.code == "MALFORMED"


def test_lone_surrogate_is_rejected_at_i_json_boundary() -> None:
    session = make_session()
    message, _, _ = make_turn()
    message["body"]["hint"] = "\ud800"

    with pytest.raises(ConformanceError) as captured:
        session.receive_turn(message, now_ms=150)

    assert captured.value.code == "MALFORMED"


def test_optional_tool_rejection_is_cached_and_changed_retry_conflicts() -> None:
    session = make_session()
    message = make_control()

    for candidate in (message, deepcopy(message)):
        with pytest.raises(ConformanceError) as captured:
            session.receive_control(candidate, now_ms=150)
        assert captured.value.code == "OPTIONAL_TOOL_UNAVAILABLE"

    changed = make_control("abort")
    with pytest.raises(ConformanceError) as captured:
        session.receive_control(changed, now_ms=150)

    assert captured.value.code == "IDEMPOTENCY_CONFLICT"


def test_session_rejects_identical_participant_ids() -> None:
    with pytest.raises(ConformanceError) as captured:
        ConformanceSession(
            game_id="match",
            game_uid="match-sub-1",
            sub_game_number=1,
            local_group_id="same",
            remote_group_id="same",
            remote_role="thief",
            agreed_configuration_sha256="a" * 64,
        )

    assert captured.value.code == "IDENTITY_MISMATCH"
