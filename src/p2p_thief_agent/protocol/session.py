"""Negotiated in-memory context composing the profile's message handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from p2p_thief_agent.protocol.profile import (
    reject,
    require_identifier,
    require_lower_hex,
    require_safe_int,
)
from p2p_thief_agent.protocol.session_audit import AuditSessionMixin
from p2p_thief_agent.protocol.session_control import ControlSessionMixin
from p2p_thief_agent.protocol.session_reveal import RevealSessionMixin
from p2p_thief_agent.protocol.session_support import SeenResults, WireBinding
from p2p_thief_agent.protocol.session_turn import TurnSessionMixin


@dataclass(slots=True)
class ConformanceSession(
    TurnSessionMixin, RevealSessionMixin, AuditSessionMixin, ControlSessionMixin
):
    """Negotiated local context with idempotent turn/reveal/audit validation."""

    game_id: str
    game_uid: str
    sub_game_number: int
    local_group_id: str
    remote_group_id: str
    remote_role: str
    agreed_configuration_sha256: str
    turn_cap: int = 35
    board_size: int = 7
    optional_control: bool = False
    next_step: int = field(default=1, init=False)
    next_reveal_step: int = field(default=1, init=False)
    technical_loss: bool = field(default=False, init=False)
    score: int | None = field(default=None, init=False)
    _seen: SeenResults = field(default_factory=dict, init=False)
    _turns: dict[int, dict[str, Any]] = field(default_factory=dict, init=False)
    _reveals: dict[int, dict[str, str]] = field(default_factory=dict, init=False)
    _closed: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Validate immutable negotiated context before accepting messages."""
        require_identifier(self.game_id, "game_id")
        require_identifier(self.game_uid, "game_uid")
        require_identifier(self.local_group_id, "local_group_id", 64)
        require_identifier(self.remote_group_id, "remote_group_id", 64)
        if self.local_group_id == self.remote_group_id:
            reject("IDENTITY_MISMATCH", "local and remote group IDs must differ")
        require_lower_hex(
            self.agreed_configuration_sha256,
            64,
            "agreed_configuration_sha256",
        )
        if self.remote_role not in {"police", "thief"}:
            reject("MALFORMED", "remote_role must be police or thief")
        if not isinstance(self.optional_control, bool):
            reject("MALFORMED", "optional_control must be a boolean")
        sub_game = require_safe_int(self.sub_game_number, "sub_game_number", 1)
        if sub_game > 6:
            reject("MALFORMED", "sub_game_number must not exceed 6")
        require_safe_int(self.turn_cap, "turn_cap", 1)
        board_size = require_safe_int(self.board_size, "board_size", 2)
        if board_size > 1_000:
            reject("MALFORMED", "board_size must not exceed 1000")

    def _wire_binding(self) -> WireBinding:
        return WireBinding(
            self.game_uid,
            self.sub_game_number,
            self.local_group_id,
            self.remote_group_id,
        )
