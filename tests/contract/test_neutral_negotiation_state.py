"""Independent mirrored negotiation, replay, and offer-idempotency evidence."""

from copy import deepcopy

from tests.contract.neutral_helpers import node_result, offer


def pair() -> tuple[dict, dict, dict]:
    """Return mirrored offers and their complete active negotiation context."""
    first = offer(
        "alpha", "beta", "mirror-game",
        proposer_role="thief", responder_role="police",
        message_id="1" * 32, negotiation_id="a" * 32,
    )
    second = offer(
        "beta", "alpha", "mirror-game",
        proposer_role="police", responder_role="thief",
        message_id="2" * 32, negotiation_id="a" * 32,
    )
    active = {
        "now_ms": 150,
        "game_id": "league-match",
        "game_uid": "mirror-game",
        "sub_game_number": 1,
        "group_a_id": "alpha",
        "group_a_role": "thief",
        "group_a_git_commit": "a" * 40,
        "group_b_id": "beta",
        "group_b_role": "police",
        "group_b_git_commit": "a" * 40,
        "agreed_configuration_sha256": first["configuration"][
            "agreed_configuration_sha256"
        ],
    }
    return first, second, active


def run(offers: list[dict], active: dict) -> dict:
    return node_result({"op": "negotiate_sequence", "active": active, "offers": offers})


def test_mirrored_pair_exact_retry_and_conflict() -> None:
    """Two directions reach ready while exact retry is cached and mutation conflicts."""
    first, second, active = pair()
    changed = deepcopy(first)
    changed["expires_at_ms"] = 199
    response = run([first, deepcopy(first), changed, second], active)

    assert response["results"][0] == response["results"][1]
    assert response["results"][2]["error"]["code"] == "IDEMPOTENCY_CONFLICT"
    assert response["results"][3]["status"] == "accepted"
    assert response["ready"] is True


def test_new_message_for_consumed_direction_is_replay() -> None:
    first, _, active = pair()
    replay = deepcopy(first)
    replay["message_id"] = "f" * 32
    response = run([first, replay], active)

    assert response["results"][1]["error"]["code"] == "REPLAYED_MESSAGE"
    assert response["ready"] is False


def test_mirrored_negotiation_id_mismatch_is_out_of_order() -> None:
    first, second, active = pair()
    second["negotiation_id"] = "b" * 32
    response = run([first, second], active)

    assert response["results"][1]["error"]["code"] == "OUT_OF_ORDER"
    assert response["ready"] is False


def test_mirrored_configuration_mismatch_rejects_before_ready() -> None:
    first, second, active = pair()
    second["configuration"]["agreed_configuration_sha256"] = "f" * 64
    response = run([first, second], active)

    assert response["results"][1]["error"]["code"] == "HASH_MISMATCH"
    assert response["ready"] is False
