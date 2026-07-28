"""Final-audit verification against previously locked public turns."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from p2p_thief_agent.protocol.canonical import JSONValue
from p2p_thief_agent.protocol.commitment import (
    audit_sha256,
    payload_respects_board,
    validate_payload,
    verify_commitment,
)
from p2p_thief_agent.protocol.profile import (
    reject,
    require_closed,
    require_lower_hex,
    require_safe_int,
)

_RECORD_KEYS = ("step", "turn_message_id", "commitment_sha256", "payload", "nonce")


def verify_audit_records(
    *,
    game_id: str,
    game_uid: str,
    sub_game_number: int,
    sender_group_id: str,
    next_step: int,
    turns: Mapping[int, Mapping[str, Any]],
    records: list[JSONValue],
    board_size: int,
) -> str:
    """Validate exact record coverage, binding, nonce uniqueness, and commitments."""
    validated: list[tuple[Mapping[str, Any], int, str, Mapping[str, Any]]] = []
    for record_value in records:
        record = require_closed(record_value, _RECORD_KEYS, "audit record")
        step = require_safe_int(record["step"], "audit record step", 1)
        require_lower_hex(record["turn_message_id"], 32, "turn_message_id")
        require_lower_hex(record["commitment_sha256"], 64, "commitment_sha256")
        nonce = require_lower_hex(record["nonce"], 32, "nonce")
        payload = validate_payload(record["payload"])
        validated.append((record, step, nonce, payload))
    expected_steps = list(range(1, next_step))
    if [item[1] for item in validated] != expected_steps:
        reject("OUT_OF_ORDER", "audit records must be complete and step-ascending")
    nonces: set[str] = set()
    for record, step, nonce, payload in validated:
        turn = turns[step]
        if nonce in nonces:
            reject("COMMITMENT_MISMATCH", "audit reuses a nonce")
        nonces.add(nonce)
        if (
            record["turn_message_id"] != turn["message_id"]
            or record["commitment_sha256"] != turn["commitment_sha256"]
            or payload["game_id"] != game_id
            or payload["game_uid"] != game_uid
            or payload["sub_game_number"] != sub_game_number
            or payload["step"] != step
            or payload["sender_group_id"] != sender_group_id
            or payload["role"] != turn["role"]
            or payload["hint"] != turn["hint"]
            or payload["barrier"] != turn["barrier"]
            or not payload_respects_board(payload, board_size)
            or not verify_commitment(payload, nonce, turn["commitment_sha256"])
        ):
            reject("COMMITMENT_MISMATCH", "audit record does not match locked turn")
    return audit_sha256(
        game_id=game_id,
        game_uid=game_uid,
        sub_game_number=sub_game_number,
        sender_group_id=sender_group_id,
        records=records,
    )
