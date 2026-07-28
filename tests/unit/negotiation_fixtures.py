"""Builders shared by closed-schema negotiation tests."""

from typing import Any

import pytest

from p2p_thief_agent.protocol.negotiation import validate_offer
from p2p_thief_agent.protocol.offers import build_offer
from p2p_thief_agent.protocol.profile import ConformanceError

POLICE = "police-7"
THIEF = "thief-9"
MESSAGE_ID = "a" * 32
NEGOTIATION_ID = "b" * 32


def offer() -> dict[str, Any]:
    """Build one valid police-to-thief offer."""
    step_zero = {
        "os": "Linux",
        "cpu_cores": 8,
        "cpu_frequency_mhz": 3200,
        "ram_mb": 16384,
        "gpu": "none",
        "vram_mb": 0,
        "llm_name": "none",
        "code_version": "1.00",
        "git_commit": "c" * 40,
        "group_id": POLICE,
        "role": "police",
        "sub_game_number": 1,
    }
    return build_offer(
        proposer_group_id=POLICE,
        proposer_role="police",
        responder_group_id=THIEF,
        responder_role="thief",
        game_id="game-1",
        game_uid="uid-1",
        sub_game_number=1,
        message_id=MESSAGE_ID,
        negotiation_id=NEGOTIATION_ID,
        sent_at_ms=1000,
        expires_at_ms=2000,
        step_zero=step_zero,
        game={"agreed_between": [POLICE, THIEF], "board_size": 7},
        rate_limits={"requests_per_second": 4},
        optional_capabilities=("receive_control",),
    )


def assert_code(
    value: object,
    code: str,
    *,
    recipient: str = THIEF,
    now: int = 1500,
) -> None:
    """Assert one stable negotiation rejection code."""
    with pytest.raises(ConformanceError) as caught:
        validate_offer(value, expected_recipient=recipient, now_ms=now)
    assert caught.value.code == code
