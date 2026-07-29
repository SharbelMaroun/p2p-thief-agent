"""Independent Node reproduction of the book Step-3 live move-reveal rules."""

import pytest

from tests.contract.conformance_fixtures import (
    NONCE_1,
    audit_record,
    make_audit,
    make_payload,
    make_reveal,
    make_turn,
)
from tests.contract.neutral_helpers import action, node_session


def code(result: dict) -> str:
    return result["error"]["code"]


def test_reveal_discloses_move_and_acknowledges() -> None:
    turn, _, _ = make_turn()
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", make_reveal(move="N")),
    ])
    reveal = response["results"][1]

    assert reveal["status"] == "revealed"
    assert reveal["step"] == 1
    assert reveal["move"] == "N"


def test_reveal_before_commit_is_out_of_order() -> None:
    response = node_session([action("receive_reveal", make_reveal())])
    assert code(response["results"][0]) == "OUT_OF_ORDER"


def test_replayed_reveal_is_replayed_message() -> None:
    turn, _, _ = make_turn()
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", make_reveal(move="N")),
        action("receive_reveal", make_reveal(move="S", message_id="b" * 32)),
    ])
    assert code(response["results"][2]) == "REPLAYED_MESSAGE"


def test_restated_hint_mismatch_is_commitment_mismatch() -> None:
    turn, _, _ = make_turn()
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", make_reveal(hint="Times Square")),
    ])
    assert code(response["results"][1]) == "COMMITMENT_MISMATCH"


@pytest.mark.parametrize("leaked", ["nonce", "position", "intent"])
def test_reveal_body_rejects_hidden_fields(leaked: str) -> None:
    turn, _, _ = make_turn()
    reveal = make_reveal()
    reveal["body"][leaked] = "00" * 16 if leaked == "nonce" else "lie"
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", reveal),
    ])
    assert code(response["results"][1]) == "PRIVATE_FIELD_LEAK"


def test_audit_move_contradicting_reveal_is_rejected() -> None:
    turn, payload, _ = make_turn()  # committed move is N
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", make_reveal(move="S")),  # live reveal lies
        action("submit_audit", make_audit([audit_record(turn, payload, NONCE_1)])),
    ])
    assert response["results"][1]["status"] == "revealed"
    assert code(response["results"][2]) == "COMMITMENT_MISMATCH"


def test_consistent_reveal_then_audit_verifies() -> None:
    turn, payload, _ = make_turn()
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", make_reveal(move="N")),
        action("submit_audit", make_audit([audit_record(turn, payload, NONCE_1)])),
    ])
    assert response["results"][2]["status"] == "verified"


def test_reveal_move_matches_python_fixture_move() -> None:
    """The independent stub echoes exactly the disclosed movement token."""
    turn, _, _ = make_turn(payload=make_payload(move="STAY", hint="Broadway"))
    response = node_session([
        action("receive_move", turn),
        action("receive_reveal", make_reveal(move="STAY", hint="Broadway")),
    ])
    assert response["results"][1]["move"] == "STAY"
