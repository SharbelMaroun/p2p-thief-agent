"""Final-audit coverage, commitment, ordering, and nonce conformance."""

from copy import deepcopy

import pytest

from p2p_thief_agent.protocol.profile import ConformanceError
from tests.contract.conformance_fixtures import (
    NONCE_1,
    NONCE_2,
    NOW_MS,
    audit_record,
    make_audit,
    make_payload,
    make_session,
    make_turn,
)


def locked_two_turns():
    """Return a session and two exact reveal records."""
    session = make_session()
    first, first_payload, _ = make_turn()
    second_payload = make_payload(2, move="E", hint="Broadway")
    second, _, _ = make_turn(2, nonce=NONCE_2, payload=second_payload)
    session.receive_turn(first, now_ms=NOW_MS)
    session.receive_turn(second, now_ms=NOW_MS)
    records = [
        audit_record(first, first_payload, NONCE_1),
        audit_record(second, second_payload, NONCE_2),
    ]
    return session, records


def test_complete_audit_verifies_and_retry_is_idempotent() -> None:
    """Every locked turn reveals once and produces a stable audit digest."""
    session, records = locked_two_turns()
    message = make_audit(records)

    first = session.submit_audit(message, now_ms=NOW_MS)
    second = session.submit_audit(deepcopy(message), now_ms=NOW_MS)

    assert first == second
    assert first["status"] == "verified"
    assert first["record_count"] == 2
    assert len(first["audit_sha256"]) == 64


@pytest.mark.parametrize("mutation", ["payload", "nonce", "commitment", "turn_id"])
def test_tampered_reveal_is_commitment_mismatch(mutation: str) -> None:
    """Every hidden or locked binding is verified at final audit."""
    session, records = locked_two_turns()
    if mutation == "payload":
        records[0]["payload"]["move"] = "S"
    elif mutation == "nonce":
        records[0]["nonce"] = "f" * 64
    elif mutation == "commitment":
        records[0]["commitment_sha256"] = "f" * 64
    else:
        records[0]["turn_message_id"] = "f" * 32

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(make_audit(records), now_ms=NOW_MS)

    assert captured.value.code == "COMMITMENT_MISMATCH"
    assert session.technical_loss is True
    assert session.score == 0


def test_reused_nonce_is_rejected() -> None:
    """A nonce may bind only one commitment within a game."""
    session, records = locked_two_turns()
    records[1]["nonce"] = records[0]["nonce"]

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(make_audit(records), now_ms=NOW_MS)

    assert captured.value.code == "COMMITMENT_MISMATCH"


@pytest.mark.parametrize("change", ["missing", "extra", "reordered"])
def test_record_coverage_and_order_fail_closed(change: str) -> None:
    """Audit must cover exactly the accepted step sequence."""
    session, records = locked_two_turns()
    if change == "missing":
        records.pop()
    elif change == "extra":
        records.append(deepcopy(records[-1]))
    else:
        records.reverse()

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(make_audit(records), now_ms=NOW_MS)

    assert captured.value.code == "OUT_OF_ORDER"


def test_audit_failure_is_cached_and_changed_retry_conflicts() -> None:
    """A first technical rejection is terminal and reserves its message ID."""
    session, records = locked_two_turns()
    invalid = make_audit(deepcopy(records))
    invalid["body"]["records"][0]["nonce"] = "f" * 64
    with pytest.raises(ConformanceError):
        session.submit_audit(invalid, now_ms=NOW_MS)

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(make_audit(records), now_ms=NOW_MS)

    assert captured.value.code == "IDEMPOTENCY_CONFLICT"
    assert session.technical_loss is True
    assert session.score == 0


def test_off_board_reveal_is_technical_loss() -> None:
    session, records = locked_two_turns()
    records[0]["payload"]["position"] = [7, 0]

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(make_audit(records), now_ms=NOW_MS)

    assert captured.value.code == "COMMITMENT_MISMATCH"
    assert session.technical_loss is True


def test_malformed_record_is_validated_before_ordering() -> None:
    """Primitive/schema faults retain precedence over sequence faults."""
    session, records = locked_two_turns()
    del records[0]["nonce"]

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(make_audit(records), now_ms=NOW_MS)

    assert captured.value.code == "MALFORMED"
