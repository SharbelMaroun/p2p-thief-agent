"""Internal closed-schema validation for Option-B negotiation offers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from p2p_thief_agent.protocol.canonical import (
    agreed_configuration_sha256,
    source_sha256,
)
from p2p_thief_agent.protocol.profile import (
    OPTIONAL_CAPABILITIES,
    PROFILE,
    REQUIRED_CAPABILITIES,
    VERSION,
    decode_source,
    reject,
    require_closed,
    require_identifier,
    require_limits,
    require_lower_hex,
    require_safe_int,
)

OFFER_KEYS = (
    "profile",
    "supported_versions",
    "negotiation_id",
    "message_id",
    "sent_at_ms",
    "expires_at_ms",
    "proposer_group_id",
    "proposer_role",
    "responder_group_id",
    "responder_role",
    "game_id",
    "game_uid",
    "sub_game_number",
    "required_capabilities",
    "optional_capabilities",
    "step_zero",
    "configuration",
)
_CONFIG_KEYS = (
    "game_source_b64",
    "game_source_sha256",
    "rate_limits_source_b64",
    "rate_limits_source_sha256",
    "agreed_configuration_sha256",
)
_STEP_ZERO_KEYS = (
    "os",
    "cpu_cores",
    "cpu_frequency_mhz",
    "ram_mb",
    "gpu",
    "vram_mb",
    "llm_name",
    "code_version",
    "git_commit",
    "group_id",
    "role",
    "sub_game_number",
)


def _step_zero(value: object, offer: Mapping[str, Any]) -> None:
    step = require_closed(value, _STEP_ZERO_KEYS, "step_zero")
    for key in ("os", "gpu", "llm_name", "code_version"):
        if not isinstance(step[key], str) or not step[key]:
            reject("MALFORMED", f"step_zero.{key} must be nonempty text")
    for key in ("cpu_cores", "cpu_frequency_mhz", "ram_mb", "vram_mb"):
        require_safe_int(step[key], f"step_zero.{key}")
    require_lower_hex(step["git_commit"], 40, "step_zero.git_commit")
    if (
        step["group_id"] != offer["proposer_group_id"]
        or step["role"] != offer["proposer_role"]
        or step["sub_game_number"] != offer["sub_game_number"]
    ):
        reject("IDENTITY_MISMATCH", "step_zero does not match the proposer binding")


def _header(offer: Mapping[str, Any], expected_recipient: str, now_ms: int) -> None:
    if offer["profile"] != PROFILE:
        reject("UNSUPPORTED_PROFILE", f"profile must be {PROFILE}")
    if offer["supported_versions"] != [VERSION]:
        reject("UNSUPPORTED_VERSION", f"supported_versions must be [{VERSION!r}]")
    require_lower_hex(offer["negotiation_id"], 32, "negotiation_id")
    require_lower_hex(offer["message_id"], 32, "message_id")
    proposer = require_identifier(offer["proposer_group_id"], "proposer_group_id", 64)
    responder = require_identifier(offer["responder_group_id"], "responder_group_id", 64)
    require_identifier(expected_recipient, "expected_recipient", 64)
    require_identifier(offer["game_id"], "game_id")
    require_identifier(offer["game_uid"], "game_uid")
    sub_game = require_safe_int(offer["sub_game_number"], "sub_game_number", 1)
    if sub_game > 6:
        reject("MALFORMED", "sub_game_number must not exceed 6")
    sent = require_safe_int(offer["sent_at_ms"], "sent_at_ms")
    expires = require_safe_int(offer["expires_at_ms"], "expires_at_ms")
    if expires <= sent:
        reject("MALFORMED", "expires_at_ms must be later than sent_at_ms")
    if now_ms > expires:
        reject("EXPIRED", "negotiation offer has expired")
    if proposer == responder or responder != expected_recipient:
        reject("IDENTITY_MISMATCH", "offer participant binding does not match")
    roles = (offer["proposer_role"], offer["responder_role"])
    if any(not isinstance(role, str) for role in roles) or set(roles) != {"police", "thief"}:
        reject("IDENTITY_MISMATCH", "participants must bind opposite police/thief roles")
    _step_zero(offer["step_zero"], offer)


def _capabilities(offer: Mapping[str, Any]) -> tuple[str, ...]:
    if offer["required_capabilities"] != list(REQUIRED_CAPABILITIES):
        reject("CAPABILITY_MISMATCH", "required capabilities do not match the profile")
    optional = offer["optional_capabilities"]
    if (
        not isinstance(optional, list)
        or any(not isinstance(item, str) for item in optional)
        or optional != sorted(set(optional))
        or any(item not in OPTIONAL_CAPABILITIES for item in optional)
    ):
        reject("CAPABILITY_MISMATCH", "optional capabilities are invalid")
    return REQUIRED_CAPABILITIES + tuple(optional)


def _configuration(offer: Mapping[str, Any]) -> tuple[str, str, str]:
    config = require_closed(offer["configuration"], _CONFIG_KEYS, "configuration")
    game_raw, game = decode_source(config["game_source_b64"], "game_source_b64")
    rate_raw, rate_limits = decode_source(
        config["rate_limits_source_b64"], "rate_limits_source_b64"
    )
    if not isinstance(game, dict) or not isinstance(rate_limits, dict):
        reject("CONFIG_MISMATCH", "configuration sources must contain JSON objects")
    participants = sorted((offer["proposer_group_id"], offer["responder_group_id"]))
    if game.get("agreed_between") != participants:
        reject("IDENTITY_MISMATCH", "game.agreed_between does not bind both participants")
    hashes = (
        source_sha256("game.json", game_raw),
        source_sha256("rate_limits.json", rate_raw),
        agreed_configuration_sha256(game, rate_limits),
    )
    keys = ("game_source_sha256", "rate_limits_source_sha256", "agreed_configuration_sha256")
    for key, expected in zip(keys, hashes, strict=True):
        require_lower_hex(config[key], 64, key)
        if config[key] != expected:
            reject("HASH_MISMATCH", f"{key} does not match the offered configuration")
    return hashes


def validate_components(
    value: object, expected_recipient: str, now_ms: int
) -> tuple[Mapping[str, Any], tuple[str, ...], tuple[str, str, str]]:
    """Return a fully checked offer plus its negotiated capabilities and hashes."""
    require_limits(value, 65_536)
    offer = require_closed(value, OFFER_KEYS, "offer")
    _header(offer, expected_recipient, require_safe_int(now_ms, "now_ms"))
    return offer, _capabilities(offer), _configuration(offer)
