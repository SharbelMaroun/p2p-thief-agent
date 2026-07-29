"""Option-B conformance constants and fail-closed validation helpers."""

from __future__ import annotations

import base64
import binascii
import re
from collections.abc import Mapping, Sequence
from typing import Any

from p2p_thief_agent.protocol.canonical import (
    JSONValue,
    canonicalize,
    loads,
)

PROFILE = "p2p-thief-option-b"
VERSION = "1.0"
REQUIRED_CAPABILITIES = ("negotiate", "receive_move", "submit_audit")
OPTIONAL_CAPABILITIES = ("receive_control",)
MAX_SAFE_INTEGER = 2**53 - 1

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_LOWER_HEX = re.compile(r"^[0-9a-f]+$")


class ConformanceError(ValueError):
    """A public conformance rejection with a stable machine-readable code."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def reject(code: str, detail: str) -> None:
    """Raise a conformance rejection."""
    raise ConformanceError(code, detail)


def require_mapping(value: object, label: str) -> Mapping[str, Any]:
    """Require an object-like mapping."""
    if not isinstance(value, Mapping):
        reject("MALFORMED", f"{label} must be an object")
    return value


def require_closed(value: object, keys: Sequence[str], label: str) -> Mapping[str, Any]:
    """Require exactly the named object fields."""
    mapping = require_mapping(value, label)
    unknown = set(mapping) - set(keys)
    missing = set(keys) - set(mapping)
    if unknown:
        reject("UNKNOWN_FIELD", f"{label} has unknown field {min(unknown)!r}")
    if missing:
        reject("MALFORMED", f"{label} is missing field {min(missing)!r}")
    return mapping


def require_identifier(value: object, label: str, maximum: int = 128) -> str:
    """Require the bounded ASCII identifier grammar."""
    if not isinstance(value, str) or len(value) > maximum or _IDENTIFIER.fullmatch(value) is None:
        reject("MALFORMED", f"{label} is not a valid identifier")
    return value


def require_lower_hex(value: object, length: int, label: str) -> str:
    """Require an exact-length lowercase hexadecimal string."""
    if not isinstance(value, str) or len(value) != length or _LOWER_HEX.fullmatch(value) is None:
        reject("MALFORMED", f"{label} must be {length} lowercase hex characters")
    return value


def require_safe_int(value: object, label: str, minimum: int = 0) -> int:
    """Require an interoperable integer in a bounded lower range."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or value > MAX_SAFE_INTEGER
    ):
        reject("MALFORMED", f"{label} must be an integer from {minimum} to {MAX_SAFE_INTEGER}")
    return value


def require_limits(value: object, maximum_bytes: int, maximum_depth: int = 64) -> None:
    """Require the profile's canonical byte and container-depth limits."""
    stack: list[tuple[object, int, bool]] = [(value, 1, False)]
    active: set[int] = set()
    while stack:
        current, depth, leaving = stack.pop()
        if not isinstance(current, (dict, list)):
            continue
        marker = id(current)
        if leaving:
            active.remove(marker)
            continue
        if marker in active:
            reject("MALFORMED", "JSON value must not contain a cycle")
        if depth > maximum_depth:
            reject("MALFORMED", f"JSON container depth must not exceed {maximum_depth}")
        active.add(marker)
        stack.append((current, depth, True))
        children = current.values() if isinstance(current, dict) else current
        stack.extend((child, depth + 1, False) for child in children)
    try:
        size = len(canonicalize(value))
    except (TypeError, ValueError, RecursionError, UnicodeError) as exc:
        raise ConformanceError("MALFORMED", "argument is not valid I-JSON") from exc
    if size > maximum_bytes:
        reject("MALFORMED", f"canonical argument exceeds {maximum_bytes} bytes")


def require_expected_hash(actual: str, expected: object | None) -> None:
    """Reject a self-consistent offer that differs from the locally selected terms."""
    if expected is None:
        return
    expected_text = require_lower_hex(expected, 64, "expected_configuration_sha256")
    if actual != expected_text:
        reject("CONFIG_MISMATCH", "offered configuration differs from selected values")


def decode_source(encoded: object, label: str) -> tuple[bytes, JSONValue]:
    """Decode canonical padded base64 containing exact RFC 8785 JSON bytes."""
    if not isinstance(encoded, str):
        reject("MALFORMED", f"{label} must be base64 text")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ConformanceError("MALFORMED", f"{label} is not canonical base64") from exc
    if base64.b64encode(raw).decode("ascii") != encoded:
        reject("MALFORMED", f"{label} is not canonical padded base64")
    try:
        value = loads(raw)
    except (TypeError, ValueError) as exc:
        raise ConformanceError("MALFORMED", f"{label} is not I-JSON") from exc
    if canonicalize(value) != raw:
        reject("CONFIG_MISMATCH", f"{label} bytes are not RFC 8785 canonical JSON")
    return raw, value


def rejection(message_id: object, error: ConformanceError) -> dict[str, object]:
    """Return the profile's common rejection acknowledgement."""
    acknowledges = (
        message_id
        if (
            isinstance(message_id, str)
            and len(message_id) == 32
            and _LOWER_HEX.fullmatch(message_id) is not None
        )
        else None
    )
    return {
        "status": "rejected",
        "acknowledges": acknowledges,
        "error": {"code": error.code, "detail": str(error)[:512], "retryable": False},
    }
