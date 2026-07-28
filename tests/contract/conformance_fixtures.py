"""Deterministic protocol fixtures shared by conformance tests."""

from copy import deepcopy

from p2p_thief_agent.protocol.commitment import commitment_sha256
from p2p_thief_agent.protocol.session import ConformanceSession

NOW_MS = 150
NONCE_1 = "00" * 16
NONCE_2 = "11" * 16


def make_session(*, optional_control: bool = False) -> ConformanceSession:
    """Return one negotiated local view of a remote Thief."""
    return ConformanceSession(
        game_id="match-01",
        game_uid="match-01-sub-1",
        sub_game_number=1,
        local_group_id="groupPolice",
        remote_group_id="groupThief",
        remote_role="thief",
        agreed_configuration_sha256="a" * 64,
        optional_control=optional_control,
    )


def make_payload(step: int = 1, *, move: str = "N", hint: str = "Central Park"):
    """Return an exact committed payload."""
    return {
        "domain": "p2p-thief/move-commitment/v1",
        "game_id": "match-01",
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "step": step,
        "sender_group_id": "groupThief",
        "role": "thief",
        "position": [3, 3],
        "move": move,
        "intent": "lie",
        "hint": hint,
        "barrier": None,
    }


def make_turn(
    step: int = 1,
    *,
    nonce: str = NONCE_1,
    message_id: str | None = None,
    payload: dict | None = None,
):
    """Return a public commitment-only turn and its hidden reveal."""
    reveal = deepcopy(payload or make_payload(step))
    turn_id = message_id or f"{step:032x}"
    commitment = commitment_sha256(reveal, nonce)
    message = {
        "profile": "p2p-thief-option-b",
        "version": "1.0",
        "message_id": turn_id,
        "sent_at_ms": 100,
        "expires_at_ms": 200,
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "sender_group_id": "groupThief",
        "recipient_group_id": "groupPolice",
        "type": "turn_commit",
        "body": {
            "step": step,
            "role": "thief",
            "commitment_sha256": commitment,
            "hint": reveal["hint"],
            "barrier": reveal["barrier"],
        },
    }
    return message, reveal, nonce


def audit_record(message: dict, payload: dict, nonce: str) -> dict:
    """Build one final reveal record for a locked turn."""
    return {
        "step": payload["step"],
        "turn_message_id": message["message_id"],
        "commitment_sha256": message["body"]["commitment_sha256"],
        "payload": deepcopy(payload),
        "nonce": nonce,
    }


def make_audit(records: list[dict], *, message_id: str = "f" * 32) -> dict:
    """Return the remote peer's final-audit envelope."""
    return {
        "profile": "p2p-thief-option-b",
        "version": "1.0",
        "message_id": message_id,
        "sent_at_ms": 100,
        "expires_at_ms": 200,
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "sender_group_id": "groupThief",
        "recipient_group_id": "groupPolice",
        "type": "final_audit",
        "body": {"records": records},
    }


def make_control(control: str = "heartbeat", *, message_id: str = "c" * 32) -> dict:
    """Return a control envelope with an exact heartbeat or abort body."""
    body = (
        {"control": "heartbeat"}
        if control == "heartbeat"
        else {"control": "abort", "code": "peer_abort", "reason": "requested"}
    )
    return {
        "profile": "p2p-thief-option-b",
        "version": "1.0",
        "message_id": message_id,
        "sent_at_ms": 100,
        "expires_at_ms": 200,
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "sender_group_id": "groupThief",
        "recipient_group_id": "groupPolice",
        "type": "control",
        "body": body,
    }
