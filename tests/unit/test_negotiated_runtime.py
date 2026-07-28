"""Negotiation readiness gates creation of a bound message session."""

import pytest

from p2p_thief_agent.protocol.negotiated_runtime import open_remote_session
from p2p_thief_agent.protocol.profile import ConformanceError
from tests.unit.negotiation_state_fixtures import incoming, outgoing, state


def test_session_cannot_open_before_both_mirrored_offers() -> None:
    negotiation = state()
    negotiation.accept(outgoing(), now_ms=150)

    with pytest.raises(ConformanceError) as captured:
        open_remote_session(negotiation, board_size=7, turn_cap=35)

    assert captured.value.code == "OUT_OF_ORDER"


def test_ready_negotiation_opens_exact_remote_binding() -> None:
    negotiation = state()
    negotiation.accept(outgoing(), now_ms=150)
    negotiation.accept(incoming(), now_ms=150)

    session = open_remote_session(negotiation, board_size=7, turn_cap=35)

    assert session.game_id == negotiation.game_id
    assert session.game_uid == negotiation.game_uid
    assert session.local_group_id == negotiation.local_group_id
    assert session.remote_group_id == negotiation.remote_group_id
    assert session.agreed_configuration_sha256 == (
        negotiation.expected_configuration_sha256
    )
    assert session.board_size == 7
    assert session.turn_cap == 35
    assert session.optional_control is True
