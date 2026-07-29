"""Move-commitment, nonce, payload, and audit-domain tests."""

import re

import pytest

from p2p_thief_agent.protocol.commitment import (
    audit_sha256,
    commitment_sha256,
    new_nonce,
    validate_payload,
    verify_commitment,
)
from p2p_thief_agent.protocol.profile import ConformanceError

NONCE = "000102030405060708090a0b0c0d0e0f"


def payload() -> dict[str, object]:
    """Return one complete deterministic Thief reveal."""
    return {
        "domain": "p2p-thief/move-commitment/v1",
        "game_id": "match-01",
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "step": 1,
        "sender_group_id": "sharNamr",
        "role": "thief",
        "position": [3, 3],
        "move": "N",
        "intent": "lie",
        "hint": "Central Park",
        "barrier": None,
    }


def test_known_commitment_vector_and_verification() -> None:
    """The simulator construction (canonical_json + "|" + nonce) has a frozen value."""
    expected = "349470332e9917b65f0ebe6dd23b63fadb18371ef5f790f50aed981a2a73cc3d"

    assert commitment_sha256(payload(), NONCE) == expected
    assert verify_commitment(payload(), NONCE, expected)


def test_changed_payload_or_nonce_does_not_verify() -> None:
    """Either part of the reveal is cryptographically bound."""
    expected = commitment_sha256(payload(), NONCE)
    changed = payload()
    changed["move"] = "S"

    assert not verify_commitment(changed, NONCE, expected)
    assert not verify_commitment(payload(), "f" * 32, expected)


def test_nonce_is_16_random_bytes_in_lower_hex() -> None:
    """Generated nonces are the book's token_hex(16): 32 lowercase hex and fresh."""
    first = new_nonce()
    second = new_nonce()

    assert re.fullmatch(r"[0-9a-f]{32}", first)
    assert first != second


@pytest.mark.parametrize(
    ("key", "bad"),
    [
        ("domain", "other"),
        ("sub_game_number", 0),
        ("step", 0),
        ("role", "cop"),
        ("position", [3]),
        ("move", "NE"),
        ("intent", "maybe"),
        ("hint", 7),
        ("barrier", {"position": [1]}),
    ],
)
def test_payload_rejects_invalid_fields(key: str, bad: object) -> None:
    """Every closed payload field is checked before hashing."""
    value = payload()
    value[key] = bad

    with pytest.raises(ConformanceError):
        validate_payload(value)


def test_payload_rejects_unknown_field_and_bad_nonce() -> None:
    """Extensions and non-profile nonce encodings fail closed."""
    value = payload()
    value["verdict"] = "win"

    with pytest.raises(ConformanceError, match="unknown field"):
        validate_payload(value)
    with pytest.raises(ConformanceError, match="32 lowercase"):
        commitment_sha256(payload(), "not-a-nonce")


def test_audit_hash_has_an_independent_domain() -> None:
    """Audit records hash with match identity and their own domain tag."""
    records = [{"step": 1, "nonce": NONCE}]

    first = audit_sha256(
        game_id="match-01",
        game_uid="match-01-sub-1",
        sub_game_number=1,
        sender_group_id="sharNamr",
        records=records,
    )
    changed = audit_sha256(
        game_id="match-01",
        game_uid="match-01-sub-2",
        sub_game_number=1,
        sender_group_id="sharNamr",
        records=records,
    )

    assert re.fullmatch(r"[0-9a-f]{64}", first)
    assert first != changed
