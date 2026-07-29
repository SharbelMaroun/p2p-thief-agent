"""Public turn ordering, idempotency, identity, and privacy conformance."""

from copy import deepcopy

import pytest

from p2p_thief_agent.protocol.profile import ConformanceError
from tests.contract.conformance_fixtures import NOW_MS, make_session, make_turn


def test_turn_is_locked_and_exact_retry_returns_cached_ack() -> None:
    """A valid commitment mutates once; an identical retry is idempotent."""
    session = make_session()
    message, _, _ = make_turn()

    first = session.receive_move(message, now_ms=NOW_MS)
    second = session.receive_move(deepcopy(message), now_ms=NOW_MS)

    assert first == second
    assert first["status"] == "locked"
    assert session.next_step == 2


def test_same_message_id_with_changed_content_is_conflict() -> None:
    """An idempotency key never aliases two different requests."""
    session = make_session()
    message, _, _ = make_turn()
    session.receive_move(message, now_ms=NOW_MS)
    changed = deepcopy(message)
    changed["body"]["hint"] = "changed"

    with pytest.raises(ConformanceError) as captured:
        session.receive_move(changed, now_ms=NOW_MS)

    assert captured.value.code == "IDEMPOTENCY_CONFLICT"
    assert session.next_step == 2


def test_new_id_replay_and_future_step_fail_without_mutation() -> None:
    """Past and future slots reject with distinct stable codes."""
    session = make_session()
    first, _, _ = make_turn()
    session.receive_move(first, now_ms=NOW_MS)
    replay, _, _ = make_turn(message_id="e" * 32)
    future, _, _ = make_turn(step=3)

    with pytest.raises(ConformanceError) as replayed:
        session.receive_move(replay, now_ms=NOW_MS)
    with pytest.raises(ConformanceError) as ordered:
        session.receive_move(future, now_ms=NOW_MS)

    assert replayed.value.code == "REPLAYED_MESSAGE"
    assert ordered.value.code == "OUT_OF_ORDER"
    assert session.next_step == 2


@pytest.mark.parametrize("field", ["payload", "nonce", "position", "move", "intent", "verdict"])
def test_private_fields_are_rejected_before_state_mutation(field: str) -> None:
    """No true reveal field is accepted in live turn traffic."""
    session = make_session()
    message, _, _ = make_turn()
    message["body"][field] = "secret"

    with pytest.raises(ConformanceError) as captured:
        session.receive_move(message, now_ms=NOW_MS)

    assert captured.value.code == "PRIVATE_FIELD_LEAK"
    assert session.next_step == 1


def test_public_barrier_position_is_the_only_position_exception() -> None:
    """A disclosed barrier location remains public by the official rule."""
    session = make_session()
    message, reveal, _ = make_turn()
    reveal["barrier"] = {"position": [3, 4]}
    message["body"]["barrier"] = {"position": [3, 4]}
    message["body"]["commitment_sha256"] = "b" * 64

    acknowledgement = session.receive_move(message, now_ms=NOW_MS)

    assert acknowledgement["status"] == "locked"


def test_public_barrier_must_be_on_negotiated_board() -> None:
    session = make_session()
    message, _, _ = make_turn()
    message["body"]["barrier"] = {"position": [7, 0]}

    with pytest.raises(ConformanceError) as captured:
        session.receive_move(message, now_ms=NOW_MS)

    assert captured.value.code == "MALFORMED"


@pytest.mark.parametrize(
    ("field", "bad", "code"),
    [
        ("version", "2.0", "UNSUPPORTED_VERSION"),
        ("recipient_group_id", "other", "IDENTITY_MISMATCH"),
        ("expires_at_ms", 120, "EXPIRED"),
    ],
)
def test_version_identity_and_expiry_fail_closed(field: str, bad: object, code: str) -> None:
    """Common-envelope failures have stable codes and no state change."""
    session = make_session()
    message, _, _ = make_turn()
    message[field] = bad

    with pytest.raises(ConformanceError) as captured:
        session.receive_move(message, now_ms=NOW_MS)

    assert captured.value.code == code
    assert session.next_step == 1
