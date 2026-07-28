"""Independent Node turn ordering, privacy, limits, and idempotency evidence."""

from copy import deepcopy

import pytest

from tests.contract.conformance_fixtures import make_turn
from tests.contract.neutral_helpers import action, node_session


def code(result: dict) -> str:
    """Return one exact rejection code."""
    assert result["status"] == "rejected"
    assert result["acknowledges"] is not None
    assert result["error"]["retryable"] is False
    return result["error"]["code"]


def test_turn_retry_conflict_replay_and_order_are_independent() -> None:
    """One Node process preserves idempotency and semantic-step state."""
    first = make_turn()[0]
    changed = deepcopy(first)
    changed["body"]["hint"] = "changed"
    replay = make_turn(message_id="e" * 32)[0]
    future = make_turn(3)[0]
    response = node_session([
        action("receive_turn", first),
        action("receive_turn", deepcopy(first)),
        action("receive_turn", changed),
        action("receive_turn", replay),
        action("receive_turn", future),
    ])

    assert response["results"][0] == response["results"][1]
    assert response["results"][0]["status"] == "locked"
    assert [code(item) for item in response["results"][2:]] == [
        "IDEMPOTENCY_CONFLICT", "REPLAYED_MESSAGE", "OUT_OF_ORDER"
    ]
    assert response["state"] == {"next_step": 2, "closed": None}


@pytest.mark.parametrize("field", ["payload", "nonce", "position", "move", "intent", "verdict"])
def test_every_early_private_field_rejects_before_lock(field: str) -> None:
    """The independent recursive scanner rejects each reserved reveal name."""
    message = make_turn()[0]
    message["body"][field] = "secret"
    response = node_session([action("receive_turn", message)])

    assert code(response["results"][0]) == "PRIVATE_FIELD_LEAK"
    assert response["state"]["next_step"] == 1


def test_public_barrier_position_is_the_only_position_exception() -> None:
    """The disclosed barrier coordinate passes strict privacy scanning."""
    message = make_turn()[0]
    message["body"]["barrier"] = {"position": [3, 4]}
    response = node_session([action("receive_turn", message)])

    assert response["results"][0]["status"] == "locked"


def test_public_barrier_coordinate_must_fit_negotiated_board() -> None:
    message = make_turn()[0]
    message["body"]["barrier"] = {"position": [7, 0]}
    response = node_session([action("receive_turn", message)])

    assert code(response["results"][0]) == "MALFORMED"


@pytest.mark.parametrize(
    ("field", "bad", "expected"),
    [
        ("version", "2.0", "UNSUPPORTED_VERSION"),
        ("recipient_group_id", "other", "IDENTITY_MISMATCH"),
        ("expires_at_ms", 120, "EXPIRED"),
        ("sent_at_ms", -0.0, "MALFORMED"),
    ],
)
def test_envelope_version_identity_expiry_and_negative_zero(
    field: str, bad: object, expected: str
) -> None:
    """Common-envelope primitives fail closed in the independent parser."""
    message = make_turn()[0]
    message[field] = bad
    response = node_session([action("receive_turn", message)])

    assert code(response["results"][0]) == expected


@pytest.mark.parametrize("limit", ["bytes", "depth"])
def test_turn_resource_limits_precede_schema(limit: str) -> None:
    message = make_turn()[0]
    if limit == "bytes":
        message["body"]["hint"] = "x" * 17_000
    else:
        nested: object = 0
        for _ in range(65):
            nested = [nested]
        message["body"]["extension"] = nested

    response = node_session([action("receive_turn", message)])

    assert code(response["results"][0]) == "MALFORMED"
