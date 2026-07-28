"""Construction of Option-B negotiation offers with canonical config sources."""

from __future__ import annotations

import base64
from collections.abc import Mapping, Sequence

from p2p_thief_agent.protocol.canonical import (
    JSONValue,
    agreed_configuration_sha256,
    canonicalize,
    source_sha256,
)
from p2p_thief_agent.protocol.profile import PROFILE, REQUIRED_CAPABILITIES, VERSION


def _encoded(value: dict[str, JSONValue]) -> str:
    return base64.b64encode(canonicalize(value)).decode("ascii")


def build_offer(
    *,
    proposer_group_id: str,
    proposer_role: str,
    responder_group_id: str,
    responder_role: str,
    game_id: str,
    game_uid: str,
    sub_game_number: int,
    message_id: str,
    negotiation_id: str,
    sent_at_ms: int,
    expires_at_ms: int,
    step_zero: Mapping[str, JSONValue],
    game: dict[str, JSONValue],
    rate_limits: dict[str, JSONValue],
    optional_capabilities: Sequence[str] = (),
) -> dict[str, JSONValue]:
    """Build canonical-source offer data; validate it before transport use."""
    game_raw = canonicalize(game)
    rate_raw = canonicalize(rate_limits)
    return {
        "profile": PROFILE,
        "supported_versions": [VERSION],
        "negotiation_id": negotiation_id,
        "message_id": message_id,
        "sent_at_ms": sent_at_ms,
        "expires_at_ms": expires_at_ms,
        "proposer_group_id": proposer_group_id,
        "proposer_role": proposer_role,
        "responder_group_id": responder_group_id,
        "responder_role": responder_role,
        "game_id": game_id,
        "game_uid": game_uid,
        "sub_game_number": sub_game_number,
        "required_capabilities": list(REQUIRED_CAPABILITIES),
        "optional_capabilities": list(optional_capabilities),
        "step_zero": dict(step_zero),
        "configuration": {
            "game_source_b64": _encoded(game),
            "game_source_sha256": source_sha256("game.json", game_raw),
            "rate_limits_source_b64": _encoded(rate_limits),
            "rate_limits_source_sha256": source_sha256("rate_limits.json", rate_raw),
            "agreed_configuration_sha256": agreed_configuration_sha256(game, rate_limits),
        },
    }
