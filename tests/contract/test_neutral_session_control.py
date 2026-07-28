"""Independent Node optional control and closed-state evidence."""

from copy import deepcopy

from tests.contract.conformance_fixtures import make_control, make_turn
from tests.contract.neutral_helpers import action, node_session


def test_unnegotiated_control_returns_exact_unavailable_rejection() -> None:
    response = node_session(
        [action("receive_control", make_control())],
        optional_control=False,
    )
    result = response["results"][0]

    assert result == {
        "status": "rejected",
        "acknowledges": "c" * 32,
        "error": {
            "code": "OPTIONAL_TOOL_UNAVAILABLE",
            "detail": "control capability was not negotiated",
            "retryable": False,
        },
    }


def test_heartbeat_retry_abort_and_closed_state() -> None:
    """Heartbeat is idempotent; abort closes turns and repeats as replay."""
    heartbeat = make_control()
    abort = make_control("abort", message_id="d" * 32)
    repeated_abort = make_control("abort", message_id="e" * 32)
    response = node_session([
        action("receive_control", heartbeat),
        action("receive_control", deepcopy(heartbeat)),
        action("receive_control", abort),
        action("receive_turn", make_turn()[0]),
        action("receive_control", repeated_abort),
    ])

    assert response["results"][0] == response["results"][1]
    assert response["results"][0]["control"] == "heartbeat"
    assert response["results"][2]["control"] == "abort"
    assert response["results"][3]["error"]["code"] == "OUT_OF_ORDER"
    assert response["results"][4]["error"]["code"] == "REPLAYED_MESSAGE"
    assert response["state"]["closed"] == "abort"


def test_control_unknown_field_and_private_leak_have_distinct_precedence() -> None:
    invalid = make_control()
    invalid["body"]["extra"] = True
    leaking = make_control(message_id="d" * 32)
    leaking["payload"] = {}
    response = node_session([
        action("receive_control", invalid),
        action("receive_control", leaking),
    ])

    assert response["results"][0]["error"]["code"] == "UNKNOWN_FIELD"
    assert response["results"][1]["error"]["code"] == "PRIVATE_FIELD_LEAK"
