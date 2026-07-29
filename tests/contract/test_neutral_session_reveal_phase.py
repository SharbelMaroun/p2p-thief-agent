"""Independent required-reveal gates and audit forward binding."""

from tests.contract.conformance_fixtures import (
    audit_record,
    make_audit,
    make_payload,
    make_reveal,
    make_turn,
)
from tests.contract.neutral_helpers import action, node_session


def test_early_audit_waits_for_live_reveal() -> None:
    """The neutral harness rejects audit until the matching Step-3 reveal."""
    turn, payload, nonce = make_turn()
    audit = make_audit([audit_record(turn, payload, nonce)])
    response = node_session([
        action("receive_move", turn),
        action("submit_audit", audit),
        action("receive_reveal", make_reveal()),
        action("submit_audit", audit),
    ])

    assert response["results"][1]["error"]["code"] == "OUT_OF_ORDER"
    assert response["results"][2]["status"] == "revealed"
    assert response["results"][3]["status"] == "verified"


def test_audit_payload_hint_must_match_the_live_reveal() -> None:
    """The independent verifier rejects a conflicting final payload hint."""
    payload = make_payload(hint="committed hint")
    turn, _, nonce = make_turn(payload=payload)
    turn["body"]["hint"] = "live hint"
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", make_reveal(hint="live hint")),
        action("submit_audit", make_audit([audit_record(turn, payload, nonce)])),
    ])

    assert response["results"][2]["error"]["code"] == "COMMITMENT_MISMATCH"
