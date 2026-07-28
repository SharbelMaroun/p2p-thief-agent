"""Reusable active-context negotiation fixtures."""

from p2p_thief_agent.protocol.canonical import agreed_configuration_sha256
from p2p_thief_agent.protocol.negotiation_state import NegotiationState
from p2p_thief_agent.protocol.offers import build_offer

LOCAL = "groupPolice"
REMOTE = "groupThief"
GAME = {"agreed_between": [LOCAL, REMOTE], "board_size": 7}
RATES = {"requests_per_second": 4}


def step_zero(group: str, role: str) -> dict[str, object]:
    """Return one exact Step-0 object."""
    return {
        "os": "Linux",
        "cpu_cores": 8,
        "cpu_frequency_mhz": 3200,
        "ram_mb": 16000,
        "gpu": "none",
        "vram_mb": 0,
        "llm_name": "none",
        "code_version": "1.00",
        "git_commit": "c" * 40,
        "group_id": group,
        "role": role,
        "sub_game_number": 1,
    }


def offer(
    proposer: str,
    proposer_role: str,
    responder: str,
    responder_role: str,
    *,
    message: str,
    negotiation: str = "a" * 32,
    game: dict | None = None,
    optional: tuple[str, ...] = ("receive_control",),
) -> dict:
    """Build a directionally valid offer."""
    return build_offer(
        proposer_group_id=proposer,
        proposer_role=proposer_role,
        responder_group_id=responder,
        responder_role=responder_role,
        game_id="match-1",
        game_uid="match-1-sub-1",
        sub_game_number=1,
        message_id=message * 32,
        negotiation_id=negotiation,
        sent_at_ms=100,
        expires_at_ms=200,
        step_zero=step_zero(proposer, proposer_role),
        game=game or GAME,
        rate_limits=RATES,
        optional_capabilities=optional,
    )


def outgoing(**kwargs) -> dict:
    """Return the local-to-remote offer."""
    return offer(LOCAL, "police", REMOTE, "thief", message="1", **kwargs)


def incoming(**kwargs) -> dict:
    """Return the remote-to-local mirror."""
    return offer(REMOTE, "thief", LOCAL, "police", message="2", **kwargs)


def state(**changes) -> NegotiationState:
    """Return one active negotiation context with optional field changes."""
    context = {
        "game_id": "match-1",
        "game_uid": "match-1-sub-1",
        "sub_game_number": 1,
        "local_group_id": LOCAL,
        "local_role": "police",
        "remote_group_id": REMOTE,
        "remote_role": "thief",
        "expected_configuration_sha256": agreed_configuration_sha256(GAME, RATES),
    }
    context.update(changes)
    return NegotiationState(**context)
