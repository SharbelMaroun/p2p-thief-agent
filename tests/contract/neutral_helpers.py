"""Shared subprocess and offer builders for independent neutral-stub tests."""

import json
import subprocess
from pathlib import Path

from p2p_thief_agent.protocol.offers import build_offer

STUB = Path(__file__).parents[1] / "neutral_stub" / "stub.js"


def node_result(command: dict) -> dict:
    """Run one black-box Node command and return its JSON result."""
    result = subprocess.run(
        ["node", str(STUB)],
        input=json.dumps(command, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def node_raw(raw: bytes) -> dict:
    """Run the neutral parser with exact bytes, including deliberately invalid input."""
    result = subprocess.run(
        ["node", str(STUB)],
        input=raw,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def _step_zero(group_id: str, role: str, sub_game: int) -> dict:
    return {
        "os": "neutral-os",
        "cpu_cores": 4,
        "cpu_frequency_mhz": 2400,
        "ram_mb": 8192,
        "gpu": "none",
        "vram_mb": 0,
        "llm_name": "none",
        "code_version": "1.00",
        "git_commit": "a" * 40,
        "group_id": group_id,
        "role": role,
        "sub_game_number": sub_game,
    }


def offer(
    proposer: str,
    responder: str,
    game_uid: str,
    *,
    proposer_role: str = "thief",
    responder_role: str = "police",
    message_id: str = "1" * 32,
    negotiation_id: str = "2" * 32,
) -> dict:
    """Build one Python-side offer with canonical config sources."""
    game = {
        "agreed_between": sorted([proposer, responder]),
        "grid": {"size": 7, "origin": "top-left"},
        "turn_cap": 35,
    }
    rate_limits = {"requests_per_minute": 30, "concurrent_requests": 2}
    return build_offer(
        proposer_group_id=proposer,
        proposer_role=proposer_role,
        responder_group_id=responder,
        responder_role=responder_role,
        game_id="league-match",
        game_uid=game_uid,
        sub_game_number=1,
        message_id=message_id,
        negotiation_id=negotiation_id,
        sent_at_ms=100,
        expires_at_ms=200,
        step_zero=_step_zero(proposer, proposer_role, 1),
        game=game,
        rate_limits=rate_limits,
        optional_capabilities=["receive_control"],
    )


def offer_context(proposed: dict, *, now_ms: int = 150) -> dict:
    """Return the complete active receiver context for an incoming offer."""
    return {
        "now_ms": now_ms,
        "game_id": proposed["game_id"],
        "game_uid": proposed["game_uid"],
        "sub_game_number": proposed["sub_game_number"],
        "local_group_id": proposed["responder_group_id"],
        "local_role": proposed["responder_role"],
        "remote_group_id": proposed["proposer_group_id"],
        "remote_role": proposed["proposer_role"],
        "agreed_configuration_sha256": proposed["configuration"][
            "agreed_configuration_sha256"
        ],
        "remote_git_commit": proposed["step_zero"]["git_commit"],
    }


def session_context(*, optional_control: bool = True) -> dict:
    """Return the negotiated context consumed by the independent state machine."""
    return {
        "game_id": "match-01",
        "game_uid": "match-01-sub-1",
        "sub_game_number": 1,
        "local_group_id": "groupPolice",
        "local_role": "police",
        "remote_group_id": "groupThief",
        "remote_role": "thief",
        "agreed_configuration_sha256": "a" * 64,
        "turn_cap": 35,
        "optional_control": optional_control,
        "axis_start_index": 0,
        "grid_size": 7,
    }


def action(tool: str, message: dict, *, now_ms: int = 150) -> dict:
    """Wrap one ordered neutral-session action."""
    return {"tool": tool, "message": message, "now_ms": now_ms}


def node_session(actions: list[dict], *, optional_control: bool = True) -> dict:
    """Run an ordered scenario through one independent Node session."""
    return node_result(
        {
            "op": "session",
            "context": session_context(optional_control=optional_control),
            "actions": actions,
        }
    )
