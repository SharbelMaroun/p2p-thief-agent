"""Required live-reveal gates and final-audit forward binding."""

import pytest

from p2p_thief_agent.protocol.profile import ConformanceError
from tests.contract.conformance_fixtures import (
    NOW_MS,
    audit_record,
    make_audit,
    make_payload,
    make_reveal,
    make_session,
    make_turn,
)


def test_early_audit_waits_for_live_reveal_without_technical_loss() -> None:
    """A locked turn cannot enter final audit before its Step-3 reveal."""
    session = make_session()
    turn, payload, nonce = make_turn()
    session.receive_move(turn, now_ms=NOW_MS)
    early = make_audit([audit_record(turn, payload, nonce)])

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(early, now_ms=NOW_MS)
    assert captured.value.code == "OUT_OF_ORDER"
    assert session.technical_loss is False
    assert session._closed is None

    session.receive_reveal(make_reveal(), now_ms=NOW_MS)
    recovery = make_audit(
        [audit_record(turn, payload, nonce)],
        message_id="e" * 32,
    )
    assert session.submit_audit(recovery, now_ms=NOW_MS)["status"] == "verified"


def test_audit_payload_hint_must_match_the_live_reveal() -> None:
    """A commitment that opens to another hint is a technical loss."""
    session = make_session()
    payload = make_payload(hint="committed hint")
    turn, _, nonce = make_turn(payload=payload)
    turn["body"]["hint"] = "live hint"
    session.receive_move(turn, now_ms=NOW_MS)
    session.receive_reveal(make_reveal(hint="live hint"), now_ms=NOW_MS)

    with pytest.raises(ConformanceError) as captured:
        session.submit_audit(
            make_audit([audit_record(turn, payload, nonce)]),
            now_ms=NOW_MS,
        )
    assert captured.value.code == "COMMITMENT_MISMATCH"
    assert session.technical_loss is True
    assert session.score == 0
