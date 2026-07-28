"""Independent Node final-audit commitment, coverage, and hash evidence."""

from copy import deepcopy

import pytest

from p2p_thief_agent.protocol.commitment import audit_sha256
from tests.contract.conformance_fixtures import (
    NONCE_1,
    NONCE_2,
    audit_record,
    make_audit,
    make_payload,
    make_turn,
)
from tests.contract.neutral_helpers import action, node_session


def scenario() -> tuple[list[dict], list[dict]]:
    """Return two public locks and their exact hidden records."""
    first, first_payload, _ = make_turn()
    second_payload = make_payload(2, move="E", hint="Broadway")
    second, _, _ = make_turn(2, nonce=NONCE_2, payload=second_payload)
    records = [
        audit_record(first, first_payload, NONCE_1),
        audit_record(second, second_payload, NONCE_2),
    ]
    return [first, second], records


def run(records: list[dict]) -> dict:
    """Lock two turns and submit the supplied records."""
    turns, _ = scenario()
    return node_session([
        action("receive_turn", turns[0]),
        action("receive_turn", turns[1]),
        action("submit_audit", make_audit(records)),
    ])


def rejection_code(response: dict) -> str:
    return response["results"][-1]["error"]["code"]


def test_complete_audit_hash_and_retry_match_python() -> None:
    """Node independently verifies records and reproduces the audit digest."""
    turns, records = scenario()
    audit = make_audit(records)
    response = node_session([
        action("receive_turn", turns[0]),
        action("receive_turn", turns[1]),
        action("submit_audit", audit),
        action("submit_audit", deepcopy(audit)),
    ])
    first, second = response["results"][2:]

    assert first == second
    assert first["status"] == "verified"
    assert first["audit_sha256"] == audit_sha256(
        game_id="match-01",
        game_uid="match-01-sub-1",
        sub_game_number=1,
        sender_group_id="groupThief",
        records=records,
    )


@pytest.mark.parametrize("mutation", ["payload", "nonce", "commitment", "turn_id", "reused"])
def test_tampered_or_reused_reveal_is_commitment_mismatch(mutation: str) -> None:
    """Every private and public lock binding is independently recomputed."""
    _, records = scenario()
    if mutation == "payload":
        records[0]["payload"]["move"] = "S"
    elif mutation == "nonce":
        records[0]["nonce"] = "f" * 64
    elif mutation == "commitment":
        records[0]["commitment_sha256"] = "f" * 64
    elif mutation == "turn_id":
        records[0]["turn_message_id"] = "f" * 32
    else:
        records[1]["nonce"] = records[0]["nonce"]

    assert rejection_code(run(records)) == "COMMITMENT_MISMATCH"


@pytest.mark.parametrize("change", ["missing", "extra", "reordered"])
def test_audit_coverage_and_order_fail_closed(change: str) -> None:
    """Records must cover the exact ascending locked sequence."""
    _, records = scenario()
    if change == "missing":
        records.pop()
    elif change == "extra":
        records.append(deepcopy(records[-1]))
    else:
        records.reverse()

    assert rejection_code(run(records)) == "OUT_OF_ORDER"


def test_failed_audit_is_not_cached_and_success_closes_streams() -> None:
    """A corrected same-ID audit succeeds; later audit/turn messages cannot."""
    turn, payload, nonce = make_turn()
    valid = make_audit([audit_record(turn, payload, nonce)])
    invalid = deepcopy(valid)
    invalid["body"]["records"][0]["nonce"] = "f" * 64
    later_turn = make_turn(2, nonce=NONCE_2)[0]
    later_audit = make_audit([], message_id="e" * 32)
    response = node_session([
        action("receive_turn", turn),
        action("submit_audit", invalid),
        action("submit_audit", valid),
        action("receive_turn", later_turn),
        action("submit_audit", later_audit),
    ])

    assert response["results"][1]["error"]["code"] == "COMMITMENT_MISMATCH"
    assert response["results"][2]["status"] == "verified"
    assert response["results"][3]["error"]["code"] == "OUT_OF_ORDER"
    assert response["results"][4]["error"]["code"] == "REPLAYED_MESSAGE"
