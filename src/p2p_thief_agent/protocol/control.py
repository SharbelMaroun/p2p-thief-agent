"""Validation for the capability-negotiated control message."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from p2p_thief_agent.protocol.profile import (
    reject,
    require_closed,
    require_identifier,
    require_mapping,
)

_HEARTBEAT_KEYS = ("control",)
_ABORT_KEYS = ("control", "code", "reason")


def validate_control_body(value: object) -> Mapping[str, Any]:
    """Validate one exact heartbeat or abort control body."""
    candidate = require_mapping(value, "body")
    control = candidate.get("control")
    if control == "heartbeat":
        return require_closed(candidate, _HEARTBEAT_KEYS, "body")
    if control != "abort":
        reject("MALFORMED", "body.control must be heartbeat or abort")
    body = require_closed(candidate, _ABORT_KEYS, "body")
    require_identifier(body["code"], "body.code", 64)
    reason = body["reason"]
    if not isinstance(reason, str) or len(reason) > 512:
        reject("MALFORMED", "body.reason must be text of at most 512 characters")
    return body
