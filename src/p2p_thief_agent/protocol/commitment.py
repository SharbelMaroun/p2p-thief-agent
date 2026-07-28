"""Book move commitments (Chapter 5.3): nonce inside the sorted, compact JSON payload.

The commitment hashes ``json.dumps(payload, sort_keys=True, separators=(",", ":"))``
with the book's default ``ensure_ascii=True`` (non-ASCII escaped), UTF-8 encoded, then
SHA-256. The nonce is a member of that payload and there is no delimiter. This matches a
book-literal opponent byte-for-byte. The separate config-hash domains keep using the
RFC 8785 JCS canonicalizer; see ``ADR-0006`` and
``COORDINATOR_RULING_COMMIT_REVEAL_2026-07-28.md``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from collections.abc import Mapping
from typing import Any

from p2p_thief_agent.protocol.canonical import JSONValue, canonicalize
from p2p_thief_agent.protocol.profile import (
    reject,
    require_closed,
    require_identifier,
    require_lower_hex,
    require_safe_int,
)

COMMITMENT_DOMAIN = "p2p-thief/move-commitment/v1"
_PAYLOAD_KEYS = (
    "domain",
    "game_id",
    "game_uid",
    "sub_game_number",
    "step",
    "sender_group_id",
    "role",
    "position",
    "move",
    "intent",
    "hint",
    "barrier",
)


def new_nonce() -> str:
    """Return 16 CSPRNG bytes as 32 lowercase hex characters (book ``token_hex(16)``)."""
    return secrets.token_hex(16)


def _position(value: object, label: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 2:
        reject("MALFORMED", f"{label} must be a two-integer array")
    return [
        require_safe_int(value[0], f"{label}[0]"),
        require_safe_int(value[1], f"{label}[1]"),
    ]


def validate_payload(value: object) -> Mapping[str, Any]:
    """Validate the exact committed payload shape without gameplay inference."""
    payload = require_closed(value, _PAYLOAD_KEYS, "payload")
    if payload["domain"] != COMMITMENT_DOMAIN:
        reject("MALFORMED", f"payload.domain must be {COMMITMENT_DOMAIN}")
    require_identifier(payload["game_id"], "payload.game_id")
    require_identifier(payload["game_uid"], "payload.game_uid")
    require_identifier(payload["sender_group_id"], "payload.sender_group_id", 64)
    sub_game = require_safe_int(payload["sub_game_number"], "payload.sub_game_number", 1)
    if sub_game > 6:
        reject("MALFORMED", "payload.sub_game_number must not exceed 6")
    require_safe_int(payload["step"], "payload.step", 1)
    if payload["role"] not in {"police", "thief"}:
        reject("MALFORMED", "payload.role must be police or thief")
    _position(payload["position"], "payload.position")
    if payload["move"] not in {"N", "S", "E", "W", "STAY"}:
        reject("MALFORMED", "payload.move is not a fixed movement token")
    if payload["intent"] not in {"truth", "lie"}:
        reject("MALFORMED", "payload.intent must be truth or lie")
    if not isinstance(payload["hint"], str) or len(payload["hint"]) > 4096:
        reject("MALFORMED", "payload.hint must be text of at most 4096 characters")
    barrier = payload["barrier"]
    if barrier is not None:
        barrier = require_closed(barrier, ("position",), "payload.barrier")
        _position(barrier["position"], "payload.barrier.position")
    return payload


def payload_respects_board(payload: Mapping[str, Any], board_size: int) -> bool:
    """Return whether positions and the declared move fit the negotiated board."""
    row, column = payload["position"]
    if row >= board_size or column >= board_size:
        return False
    offsets = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1), "STAY": (0, 0)}
    row_delta, column_delta = offsets[payload["move"]]
    if not (0 <= row + row_delta < board_size):
        return False
    if not (0 <= column + column_delta < board_size):
        return False
    barrier = payload["barrier"]
    return barrier is None or all(cell < board_size for cell in barrier["position"])


def _book_canonical_bytes(committed: Mapping[str, Any]) -> bytes:
    """Serialize exactly as book Chapter 5.3: sorted keys, compact, escaped, UTF-8."""
    return json.dumps(dict(committed), sort_keys=True, separators=(",", ":")).encode("utf-8")


def commitment_sha256(payload: object, nonce: object) -> str:
    """Hash the book payload with the nonce inside it and no delimiter (Ch.5.3)."""
    validated = validate_payload(payload)
    nonce_text = require_lower_hex(nonce, 32, "nonce")
    committed = {**dict(validated), "nonce": nonce_text}
    return hashlib.sha256(_book_canonical_bytes(committed)).hexdigest()


def verify_commitment(payload: object, nonce: object, expected: object) -> bool:
    """Return whether a reveal matches an exact lowercase SHA-256 commitment."""
    expected_text = require_lower_hex(expected, 64, "commitment_sha256")
    return hmac.compare_digest(commitment_sha256(payload, nonce), expected_text)


def audit_sha256(
    *,
    game_id: str,
    game_uid: str,
    sub_game_number: int,
    sender_group_id: str,
    records: list[JSONValue],
) -> str:
    """Hash the exact final-audit record list in its own domain."""
    value: dict[str, JSONValue] = {
        "domain": "p2p-thief/final-audit/v1",
        "game_id": game_id,
        "game_uid": game_uid,
        "sub_game_number": sub_game_number,
        "sender_group_id": sender_group_id,
        "records": records,
    }
    return hashlib.sha256(canonicalize(value)).hexdigest()
