"""Strict public turn-message validation and private-field leakage rejection."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from p2p_thief_agent.protocol.profile import (
    reject,
    require_closed,
    require_lower_hex,
    require_safe_int,
)

_TURN_KEYS = ("step", "role", "commitment_sha256", "hint", "barrier")
_PRIVATE_FIELDS = {"payload", "nonce", "position", "move", "intent", "verdict"}


def reject_private_fields(value: object, path: tuple[str, ...] = ()) -> None:
    """Reject reserved private member names before ordinary schema validation."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            is_public_barrier = child_path == ("body", "barrier", "position")
            if key in _PRIVATE_FIELDS and not is_public_barrier:
                reject("PRIVATE_FIELD_LEAK", f"private field {'.'.join(child_path)}")
            reject_private_fields(child, child_path)
    elif isinstance(value, list):
        for child in value:
            reject_private_fields(child, path)


def _public_barrier(value: object, board_size: int) -> None:
    if value is None:
        return
    barrier = require_closed(value, ("position",), "body.barrier")
    position = barrier["position"]
    if not isinstance(position, list) or len(position) != 2:
        reject("MALFORMED", "body.barrier.position must be a two-integer array")
    row = require_safe_int(position[0], "body.barrier.position[0]")
    column = require_safe_int(position[1], "body.barrier.position[1]")
    if row >= board_size or column >= board_size:
        reject("MALFORMED", "body.barrier.position must be on the negotiated board")


def validate_turn_body(value: object, *, expected_role: str, board_size: int) -> Mapping[str, Any]:
    """Validate the public commitment-only body without session-order mutation."""
    body = require_closed(value, _TURN_KEYS, "body")
    require_safe_int(body["step"], "body.step", 1)
    if body["role"] != expected_role:
        reject("IDENTITY_MISMATCH", "turn role does not match sender")
    require_lower_hex(body["commitment_sha256"], 64, "body.commitment_sha256")
    if not isinstance(body["hint"], str) or len(body["hint"]) > 4096:
        reject("MALFORMED", "body.hint must be text of at most 4096 characters")
    _public_barrier(body["barrier"], board_size)
    return body
