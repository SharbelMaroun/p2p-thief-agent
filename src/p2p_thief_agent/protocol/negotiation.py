"""Pure Option-B negotiation offer construction and validation."""

from __future__ import annotations

from dataclasses import dataclass

from p2p_thief_agent.protocol._offer_validation import OFFER_KEYS, validate_components
from p2p_thief_agent.protocol.canonical import JSONValue
from p2p_thief_agent.protocol.profile import (
    PROFILE,
    VERSION,
    require_closed,
    require_expected_hash,
)


@dataclass(frozen=True, slots=True)
class NegotiatedOffer:
    """Validated values used to form an acceptance acknowledgement."""

    participants: tuple[dict[str, str], dict[str, str]]
    capabilities: tuple[str, ...]
    game_source_sha256: str
    rate_limits_source_sha256: str
    agreed_configuration_sha256: str


def validate_offer(value: object, *, expected_recipient: str, now_ms: int) -> NegotiatedOffer:
    """Validate a closed negotiation offer without mutating runtime state."""
    offer, capabilities, hashes = validate_components(value, expected_recipient, now_ms)
    participants = (
        {"group_id": offer["proposer_group_id"], "role": offer["proposer_role"]},
        {"group_id": offer["responder_group_id"], "role": offer["responder_role"]},
    )
    return NegotiatedOffer(participants, capabilities, *hashes)


def accept_offer(
    value: object,
    *,
    expected_recipient: str,
    now_ms: int,
    expected_configuration_sha256: str | None = None,
) -> dict[str, JSONValue]:
    """Return the exact success acknowledgement for a valid offer."""
    accepted = validate_offer(value, expected_recipient=expected_recipient, now_ms=now_ms)
    offer = require_closed(value, OFFER_KEYS, "offer")
    require_expected_hash(accepted.agreed_configuration_sha256, expected_configuration_sha256)
    return {
        "profile": PROFILE,
        "version": VERSION,
        "status": "accepted",
        "acknowledges": offer["message_id"],
        "negotiation_id": offer["negotiation_id"],
        "game_id": offer["game_id"],
        "game_uid": offer["game_uid"],
        "sub_game_number": offer["sub_game_number"],
        "participants": list(accepted.participants),
        "accepted_capabilities": list(accepted.capabilities),
        "game_source_sha256": accepted.game_source_sha256,
        "rate_limits_source_sha256": accepted.rate_limits_source_sha256,
        "agreed_configuration_sha256": accepted.agreed_configuration_sha256,
    }
