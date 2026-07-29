"""Book Step-3 live move-reveal ordering, privacy, and audit forward-binding."""

from copy import deepcopy

import pytest

from p2p_thief_agent.protocol.profile import ConformanceError
from tests.contract.conformance_fixtures import (
    NONCE_1,
    NOW_MS,
    audit_record,
    make_audit,
    make_reveal,
    make_session,
    make_turn,
)


def committed():
    """Return a session with one locked step-1 commitment."""
    session = make_session()
    turn, payload, _ = make_turn()
    session.receive_move(turn, now_ms=NOW_MS)
    return session, payload


def test_reveal_discloses_move_and_keeps_nonce_hidden() -> None:
    session, _ = committed()
    result = session.receive_reveal(make_reveal(move="N"), now_ms=NOW_MS)

    assert result["status"] == "revealed"
    assert result["step"] == 1
    assert result["move"] == "N"
    assert session._reveals == {1: {"move": "N", "hint": "Central Park"}}


def test_reveal_before_commit_is_out_of_order() -> None:
    session = make_session()
    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(make_reveal(), now_ms=NOW_MS)
    assert captured.value.code == "OUT_OF_ORDER"


def test_reveal_out_of_sequence_is_out_of_order() -> None:
    session, _ = committed()
    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(make_reveal(2), now_ms=NOW_MS)
    assert captured.value.code == "OUT_OF_ORDER"


def test_semantic_reveal_retry_acknowledges_or_conflicts_deterministically() -> None:
    session, _ = committed()
    first = session.receive_reveal(make_reveal(move="N"), now_ms=NOW_MS)
    repeated = session.receive_reveal(
        make_reveal(move="N", message_id="b" * 32), now_ms=NOW_MS
    )

    assert repeated["status"] == "revealed"
    assert repeated["acknowledges"] == "b" * 32
    assert repeated["move"] == first["move"]
    assert session.next_reveal_step == 2

    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(
            make_reveal(move="S", message_id="c" * 32), now_ms=NOW_MS
        )
    assert captured.value.code == "COMMITMENT_MISMATCH"
    assert session.technical_loss is False
    assert session._closed is None


def test_exact_retry_is_idempotent_and_conflict_is_detected() -> None:
    session, _ = committed()
    reveal = make_reveal(move="N")
    first = session.receive_reveal(reveal, now_ms=NOW_MS)
    again = session.receive_reveal(deepcopy(reveal), now_ms=NOW_MS)
    assert first == again

    conflict = dict(reveal)
    conflict["body"] = {"step": 1, "move": "S", "hint": "Central Park"}
    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(conflict, now_ms=NOW_MS)
    assert captured.value.code == "IDEMPOTENCY_CONFLICT"


def test_restated_hint_must_match_locked_turn() -> None:
    session, _ = committed()
    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(make_reveal(hint="Times Square"), now_ms=NOW_MS)
    assert captured.value.code == "COMMITMENT_MISMATCH"


@pytest.mark.parametrize("leaked", ["nonce", "position", "intent"])
def test_reveal_body_rejects_still_hidden_fields(leaked: str) -> None:
    session, _ = committed()
    reveal = make_reveal()
    reveal["body"][leaked] = "00" * 16 if leaked == "nonce" else "lie"
    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(reveal, now_ms=NOW_MS)
    assert captured.value.code == "PRIVATE_FIELD_LEAK"


def test_bad_move_token_is_malformed() -> None:
    session, _ = committed()
    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(make_reveal(move="NW"), now_ms=NOW_MS)
    assert captured.value.code == "MALFORMED"


def test_reveal_after_audit_close_is_out_of_order() -> None:
    session, payload = committed()
    session.receive_reveal(make_reveal(move="N"), now_ms=NOW_MS)
    turn, _, _ = make_turn()
    session.submit_audit(
        make_audit([audit_record(turn, payload, NONCE_1)]), now_ms=NOW_MS
    )
    with pytest.raises(ConformanceError) as captured:
        session.receive_reveal(
            make_reveal(2, message_id="c" * 32), now_ms=NOW_MS
        )
    assert captured.value.code == "OUT_OF_ORDER"


def test_audit_move_contradicting_reveal_is_technical_loss() -> None:
    session, payload = committed()  # committed move is N
    session.receive_reveal(make_reveal(move="S"), now_ms=NOW_MS)  # live reveal lies
    turn, _, _ = make_turn()  # audit must disclose the committed move N
    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(
            make_audit([audit_record(turn, payload, NONCE_1)]), now_ms=NOW_MS
        )
    assert captured.value.code == "COMMITMENT_MISMATCH"
    assert session.technical_loss is True


def test_consistent_reveal_then_audit_verifies() -> None:
    session, payload = committed()
    session.receive_reveal(make_reveal(move="N"), now_ms=NOW_MS)
    turn, _, _ = make_turn()
    result = session.submit_audit(
        make_audit([audit_record(turn, payload, NONCE_1)]), now_ms=NOW_MS
    )
    assert result["status"] == "verified"
