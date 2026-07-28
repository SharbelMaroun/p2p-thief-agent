"""Stateful binding for the two mirrored Option-B negotiation offers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from p2p_thief_agent.protocol.canonical import JSONValue, canonical_sha256
from p2p_thief_agent.protocol.negotiation import accept_offer
from p2p_thief_agent.protocol.profile import (
    ConformanceError,
    reject,
    require_identifier,
    require_lower_hex,
    require_mapping,
    require_safe_int,
)


@dataclass(slots=True)
class NegotiationState:
    """Bind offers to one active match and become ready after both directions."""

    game_id: str
    game_uid: str
    sub_game_number: int
    local_group_id: str
    local_role: str
    remote_group_id: str
    remote_role: str
    expected_configuration_sha256: str
    _seen: dict[
        tuple[str, str],
        tuple[str, dict[str, JSONValue] | tuple[str, str]],
    ] = field(
        default_factory=dict, init=False
    )
    _accepted: dict[str, dict[str, JSONValue]] = field(default_factory=dict, init=False)
    _mirror: tuple[object, ...] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Validate the complete active context before receiving an offer."""
        require_identifier(self.game_id, "game_id")
        require_identifier(self.game_uid, "game_uid")
        require_identifier(self.local_group_id, "local_group_id", 64)
        require_identifier(self.remote_group_id, "remote_group_id", 64)
        sub_game = require_safe_int(self.sub_game_number, "sub_game_number", 1)
        if sub_game > 6:
            reject("MALFORMED", "sub_game_number must not exceed 6")
        roles = (self.local_role, self.remote_role)
        invalid_roles = any(not isinstance(role, str) for role in roles)
        if (
            self.local_group_id == self.remote_group_id
            or invalid_roles
            or set(roles) != {"police", "thief"}
        ):
            reject("IDENTITY_MISMATCH", "active participants and roles must be opposite")
        require_lower_hex(self.expected_configuration_sha256, 64, "expected_configuration_sha256")

    @property
    def ready(self) -> bool:
        """Return whether both mirrored directions have been accepted."""
        return set(self._accepted) == {"local", "remote"}

    def _direction(self, offer: Any) -> str:
        proposer = offer["proposer_group_id"]
        responder = offer["responder_group_id"]
        roles = (offer["proposer_role"], offer["responder_role"])
        if (proposer, responder, *roles) == (
            self.local_group_id,
            self.remote_group_id,
            self.local_role,
            self.remote_role,
        ):
            return "local"
        if (proposer, responder, *roles) == (
            self.remote_group_id,
            self.local_group_id,
            self.remote_role,
            self.local_role,
        ):
            return "remote"
        reject("IDENTITY_MISMATCH", "offer does not match the active participants and roles")

    def _cache_error(
        self,
        key: tuple[str, str],
        fingerprint: str,
        error: ConformanceError,
    ) -> None:
        cached = self._seen.get(key)
        if cached is not None and cached[0] != fingerprint:
            reject("IDEMPOTENCY_CONFLICT", "offer message_id has different content")
        if cached is None:
            self._seen[key] = (fingerprint, (error.code, str(error)))

    def accept(self, value: object, *, now_ms: int) -> dict[str, JSONValue]:
        """Validate, acknowledge, and record one direction idempotently."""
        candidate = require_mapping(value, "offer")
        expected_recipient = (
            self.remote_group_id
            if candidate.get("proposer_group_id") == self.local_group_id
            else self.local_group_id
        )
        try:
            fingerprint = canonical_sha256(
                {"domain": "p2p-thief/idempotency/v1", "message": dict(candidate)}
            )
        except (TypeError, ValueError):
            fingerprint = None
        proposer = candidate.get("proposer_group_id")
        message_id = candidate.get("message_id")
        key = (
            (proposer, message_id)
            if isinstance(proposer, str) and isinstance(message_id, str)
            else None
        )
        try:
            acknowledgement = accept_offer(
                value,
                expected_recipient=expected_recipient,
                now_ms=now_ms,
                expected_configuration_sha256=self.expected_configuration_sha256,
            )
            if (
                candidate["game_id"] != self.game_id
                or candidate["game_uid"] != self.game_uid
                or candidate["sub_game_number"] != self.sub_game_number
            ):
                reject("IDENTITY_MISMATCH", "offer does not match the active game identity")
            direction = self._direction(candidate)
        except ConformanceError as error:
            if key is not None and fingerprint is not None:
                self._cache_error(key, fingerprint, error)
            raise
        if key is None or fingerprint is None:
            reject("MALFORMED", "offer idempotency fields are invalid")
        cached = self._seen.get(key)
        if cached is not None:
            if cached[0] != fingerprint:
                reject("IDEMPOTENCY_CONFLICT", "offer message_id has different content")
            result = cached[1]
            if isinstance(result, tuple):
                raise ConformanceError(*result)
            return result
        mirror = (
            candidate["negotiation_id"],
            tuple(acknowledgement["accepted_capabilities"]),
            acknowledgement["game_source_sha256"],
            acknowledgement["rate_limits_source_sha256"],
            acknowledgement["agreed_configuration_sha256"],
        )
        if self._mirror is not None and mirror != self._mirror:
            reject("OUT_OF_ORDER", "mirrored offers do not describe one negotiation")
        if direction in self._accepted:
            reject("REPLAYED_MESSAGE", "offer direction was already accepted")
        self._mirror = mirror
        self._accepted[direction] = acknowledgement
        self._seen[key] = (fingerprint, acknowledgement)
        return acknowledgement
