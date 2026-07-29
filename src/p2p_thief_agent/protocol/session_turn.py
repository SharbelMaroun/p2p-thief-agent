"""Turn handler mixin for the in-memory conformance session."""

from __future__ import annotations

from typing import Any

from p2p_thief_agent.protocol.canonical import JSONValue
from p2p_thief_agent.protocol.messages import validate_turn_body
from p2p_thief_agent.protocol.profile import PROFILE, VERSION, ConformanceError, reject
from p2p_thief_agent.protocol.session_support import (
    cached,
    remember_error,
    remember_success,
    validate_envelope,
)


class TurnSessionMixin:
    """Provide fail-closed, idempotent turn commitment handling."""

    def receive_move(self, value: object, *, now_ms: int) -> dict[str, JSONValue]:
        """Validate and durably lock one commitment-only turn message."""
        message = validate_envelope(
            value,
            "turn_commit",
            now_ms,
            maximum_bytes=16_384,
            scan_private=True,
            binding=self._wire_binding(),  # type: ignore[attr-defined]
        )
        try:
            body = validate_turn_body(
                message["body"],
                expected_role=self.remote_role,  # type: ignore[attr-defined]
                board_size=self.board_size,  # type: ignore[attr-defined]
            )
            prior = cached(self._seen, message)  # type: ignore[attr-defined]
            if prior is not None:
                return prior
            if self._closed is not None:  # type: ignore[attr-defined]
                reject("OUT_OF_ORDER", "turn stream is already closed")
            step = body["step"]
            if step < self.next_step:  # type: ignore[attr-defined]
                reject("REPLAYED_MESSAGE", "turn step was already accepted")
            if self.next_reveal_step < self.next_step:  # type: ignore[attr-defined]
                reject("OUT_OF_ORDER", "previous turn is awaiting its live reveal")
            if (
                step > self.next_step  # type: ignore[attr-defined]
                or step > self.turn_cap  # type: ignore[attr-defined]
            ):
                reject("OUT_OF_ORDER", "turn step is not the next expected step")
        except ConformanceError as error:
            remember_error(self._seen, message, error)  # type: ignore[attr-defined]
            raise
        acknowledgement: dict[str, JSONValue] = {
            "profile": PROFILE,
            "version": VERSION,
            "status": "locked",
            "acknowledges": message["message_id"],
            "game_uid": self.game_uid,  # type: ignore[attr-defined]
            "sub_game_number": self.sub_game_number,  # type: ignore[attr-defined]
            "step": step,
            "commitment_sha256": body["commitment_sha256"],
        }
        turn: dict[str, Any] = {"message_id": message["message_id"], **dict(body)}
        self._turns[step] = turn  # type: ignore[attr-defined]
        self.next_step += 1  # type: ignore[attr-defined]
        return remember_success(self._seen, message, acknowledgement)  # type: ignore[attr-defined]
