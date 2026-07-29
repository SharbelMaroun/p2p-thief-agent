"""Shared envelope and idempotency mechanics for conformance sessions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from p2p_thief_agent.protocol.canonical import JSONValue, canonical_sha256
from p2p_thief_agent.protocol.messages import reject_private_fields
from p2p_thief_agent.protocol.profile import (
    PROFILE,
    VERSION,
    ConformanceError,
    reject,
    require_closed,
    require_identifier,
    require_limits,
    require_lower_hex,
    require_safe_int,
)

_ENVELOPE_KEYS = (
    "profile",
    "version",
    "message_id",
    "sent_at_ms",
    "expires_at_ms",
    "game_uid",
    "sub_game_number",
    "sender_group_id",
    "recipient_group_id",
    "type",
    "body",
)


@dataclass(frozen=True, slots=True)
class WireBinding:
    """Identity fields fixed by an accepted negotiation."""

    game_uid: str
    sub_game_number: int
    local_group_id: str
    remote_group_id: str


@dataclass(frozen=True, slots=True)
class CachedError:
    """Stable cached application rejection."""

    code: str
    detail: str


CachedResult = dict[str, JSONValue] | CachedError
SeenResults = dict[str, tuple[str, CachedResult]]


def validate_envelope(
    value: object,
    expected_type: str,
    now_ms: int,
    *,
    maximum_bytes: int,
    scan_private: bool,
    binding: WireBinding,
    allow_private_paths: tuple[tuple[str, ...], ...] = (),
) -> dict[str, Any]:
    """Validate the common envelope through identity, expiry, and message type."""
    require_limits(value, maximum_bytes)
    if scan_private:
        reject_private_fields(value, allow=allow_private_paths)
    message = dict(require_closed(value, _ENVELOPE_KEYS, "message"))
    if message["profile"] != PROFILE:
        reject("UNSUPPORTED_PROFILE", "message profile does not match")
    if message["version"] != VERSION:
        reject("UNSUPPORTED_VERSION", "message version does not match")
    require_lower_hex(message["message_id"], 32, "message_id")
    game_uid = require_identifier(message["game_uid"], "game_uid")
    sub_game = require_safe_int(message["sub_game_number"], "sub_game_number", 1)
    sender = require_identifier(message["sender_group_id"], "sender_group_id", 64)
    recipient = require_identifier(message["recipient_group_id"], "recipient_group_id", 64)
    sent = require_safe_int(message["sent_at_ms"], "sent_at_ms")
    expires = require_safe_int(message["expires_at_ms"], "expires_at_ms")
    if expires <= sent:
        reject("MALFORMED", "expires_at_ms must be later than sent_at_ms")
    if (
        game_uid != binding.game_uid
        or sub_game != binding.sub_game_number
        or sender != binding.remote_group_id
        or recipient != binding.local_group_id
    ):
        reject("IDENTITY_MISMATCH", "message identity binding does not match session")
    if require_safe_int(now_ms, "now_ms") > expires:
        reject("EXPIRED", "message has expired")
    if not isinstance(message["type"], str):
        reject("MALFORMED", "message type must be text")
    if message["type"] != expected_type:
        reject("OUT_OF_ORDER", f"expected message type {expected_type}")
    return message


def _fingerprint(message: dict[str, Any]) -> str:
    return canonical_sha256({"domain": "p2p-thief/idempotency/v1", "message": message})


def cached(seen: SeenResults, message: dict[str, Any]) -> dict[str, JSONValue] | None:
    """Return an exact cached success or raise the exact cached rejection."""
    stored = seen.get(message["message_id"])
    if stored is None:
        return None
    if stored[0] != _fingerprint(message):
        reject("IDEMPOTENCY_CONFLICT", "message_id was reused with different content")
    if isinstance(stored[1], CachedError):
        raise ConformanceError(stored[1].code, stored[1].detail)
    return stored[1]


def remember_success(
    seen: SeenResults,
    message: dict[str, Any],
    acknowledgement: dict[str, JSONValue],
) -> dict[str, JSONValue]:
    """Cache and return one accepted result."""
    seen[message["message_id"]] = (_fingerprint(message), acknowledgement)
    return acknowledgement


def remember_error(seen: SeenResults, message: dict[str, Any], error: ConformanceError) -> None:
    """Cache one deterministic rejection, detecting changed-content reuse."""
    stored = seen.get(message["message_id"])
    digest = _fingerprint(message)
    if stored is not None and stored[0] != digest:
        reject("IDEMPOTENCY_CONFLICT", "message_id was reused with different content")
    if stored is None:
        seen[message["message_id"]] = (digest, CachedError(error.code, str(error)))
