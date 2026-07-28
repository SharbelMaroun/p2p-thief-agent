"""Closed-schema Option-B negotiation offer and acknowledgement tests."""

import base64

import pytest

from p2p_thief_agent.protocol.canonical import canonicalize
from p2p_thief_agent.protocol.negotiation import accept_offer, validate_offer
from p2p_thief_agent.protocol.profile import (
    PROFILE,
    REQUIRED_CAPABILITIES,
    VERSION,
    ConformanceError,
    rejection,
)
from tests.unit.negotiation_fixtures import (
    MESSAGE_ID,
    NEGOTIATION_ID,
    POLICE,
    THIEF,
    assert_code,
    offer,
)


def test_build_validate_and_accept_exact_acknowledgement() -> None:
    """A valid built offer preserves exact participant, role, capability, and hash bindings."""
    candidate = offer()
    negotiated = validate_offer(candidate, expected_recipient=THIEF, now_ms=1500)
    config = candidate["configuration"]
    acknowledgement = accept_offer(candidate, expected_recipient=THIEF, now_ms=1500)

    assert negotiated.participants == (
        {"group_id": POLICE, "role": "police"},
        {"group_id": THIEF, "role": "thief"},
    )
    assert acknowledgement == {
        "profile": PROFILE,
        "version": VERSION,
        "status": "accepted",
        "acknowledges": MESSAGE_ID,
        "negotiation_id": NEGOTIATION_ID,
        "game_id": "game-1",
        "game_uid": "uid-1",
        "sub_game_number": 1,
        "participants": list(negotiated.participants),
        "accepted_capabilities": [*REQUIRED_CAPABILITIES, "receive_control"],
        "game_source_sha256": config["game_source_sha256"],
        "rate_limits_source_sha256": config["rate_limits_source_sha256"],
        "agreed_configuration_sha256": config["agreed_configuration_sha256"],
    }


@pytest.mark.parametrize(
    ("updates", "recipient", "now", "code"),
    [
        ({}, "another-group", 1500, "IDENTITY_MISMATCH"),
        ({"responder_role": "police"}, THIEF, 1500, "IDENTITY_MISMATCH"),
        ({"proposer_role": []}, THIEF, 1500, "IDENTITY_MISMATCH"),
        ({"supported_versions": ["2.0"]}, THIEF, 1500, "UNSUPPORTED_VERSION"),
        ({"required_capabilities": []}, THIEF, 1500, "CAPABILITY_MISMATCH"),
        ({"optional_capabilities": [[]]}, THIEF, 1500, "CAPABILITY_MISMATCH"),
        ({}, THIEF, 2001, "EXPIRED"),
        ({"proposer_group_id": "bad id"}, THIEF, 1500, "MALFORMED"),
        ({"unexpected": True}, THIEF, 1500, "UNKNOWN_FIELD"),
    ],
)
def test_header_failures_reject_closed(
    updates: dict[str, object], recipient: str, now: int, code: str
) -> None:
    """Header, identity, expiry, version, capability, and closed-schema faults reject."""
    candidate = offer()
    candidate.update(updates)
    assert_code(candidate, code, recipient=recipient, now=now)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("game_source_sha256", "0" * 64),
        ("rate_limits_source_sha256", "0" * 64),
        ("agreed_configuration_sha256", "0" * 64),
    ],
)
def test_changed_configuration_hashes_reject(field: str, value: str) -> None:
    """Every separated configuration hash is independently checked."""
    candidate = offer()
    candidate["configuration"][field] = value
    assert_code(candidate, "HASH_MISMATCH")


def test_changed_and_noncanonical_sources_reject() -> None:
    """Changed canonical source and semantically valid noncanonical bytes both fail closed."""
    changed = offer()
    game = {"agreed_between": [POLICE, THIEF], "board_size": 9}
    changed["configuration"]["game_source_b64"] = base64.b64encode(canonicalize(game)).decode()
    assert_code(changed, "HASH_MISMATCH")

    noncanonical = offer()
    raw = b'{ "agreed_between": ["police-7", "thief-9"], "board_size": 7 }'
    noncanonical["configuration"]["game_source_b64"] = base64.b64encode(raw).decode()
    assert_code(noncanonical, "CONFIG_MISMATCH")


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("cpu_cores", True, "MALFORMED"),
        ("group_id", "other-group", "IDENTITY_MISMATCH"),
    ],
)
def test_malformed_or_mismatched_step_zero_rejects(field: str, value: object, code: str) -> None:
    """Step-0 resource types and proposer binding are validated."""
    candidate = offer()
    candidate["step_zero"][field] = value
    assert_code(candidate, code)


def test_common_rejection_shape_is_stable() -> None:
    """Failures use one bounded, non-retryable acknowledgement shape."""
    error = ConformanceError("EXPIRED", "offer expired")
    assert rejection(MESSAGE_ID, error) == {
        "status": "rejected",
        "acknowledges": MESSAGE_ID,
        "error": {"code": "EXPIRED", "detail": "offer expired", "retryable": False},
    }
    assert rejection(None, error)["acknowledges"] is None
