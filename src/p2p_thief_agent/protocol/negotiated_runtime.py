"""Safe transition from completed negotiation to remote-message handling."""

from __future__ import annotations

from typing import cast

from p2p_thief_agent.protocol.negotiation_state import NegotiationState
from p2p_thief_agent.protocol.profile import reject
from p2p_thief_agent.protocol.session import ConformanceSession


def open_remote_session(
    negotiation: NegotiationState,
    *,
    board_size: int,
    turn_cap: int,
) -> ConformanceSession:
    """Open the remote sender stream only after both offers are accepted."""
    if not negotiation.ready or negotiation._mirror is None:
        reject("OUT_OF_ORDER", "both mirrored offers must be accepted before gameplay")
    capabilities = cast(tuple[str, ...], negotiation._mirror[1])
    return ConformanceSession(
        game_id=negotiation.game_id,
        game_uid=negotiation.game_uid,
        sub_game_number=negotiation.sub_game_number,
        local_group_id=negotiation.local_group_id,
        remote_group_id=negotiation.remote_group_id,
        remote_role=negotiation.remote_role,
        agreed_configuration_sha256=negotiation.expected_configuration_sha256,
        turn_cap=turn_cap,
        board_size=board_size,
        optional_control="receive_control" in capabilities,
    )
