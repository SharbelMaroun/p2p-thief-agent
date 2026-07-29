"""Live move-reveal (book Step 3) handler mixin for the conformance session."""

from __future__ import annotations

from p2p_thief_agent.protocol.canonical import JSONValue
from p2p_thief_agent.protocol.messages import validate_reveal_body
from p2p_thief_agent.protocol.profile import PROFILE, VERSION, ConformanceError, reject
from p2p_thief_agent.protocol.session_support import (
    cached,
    remember_error,
    remember_success,
    validate_envelope,
)


class RevealSessionMixin:
    """Disclose the move for a locked step while the nonce stays hidden until audit."""

    def receive_reveal(self, value: object, *, now_ms: int) -> dict[str, JSONValue]:
        """Validate and durably record one live move reveal (Step 3)."""
        message = validate_envelope(
            value,
            "move_reveal",
            now_ms,
            maximum_bytes=16_384,
            scan_private=True,
            binding=self._wire_binding(),  # type: ignore[attr-defined]
            allow_private_paths=(("body", "move"),),
        )
        try:
            body = validate_reveal_body(message["body"])
            prior = cached(self._seen, message)  # type: ignore[attr-defined]
            if prior is not None:
                return prior
            if self._closed is not None:  # type: ignore[attr-defined]
                reject("OUT_OF_ORDER", "reveal stream is already closed")
            step = body["step"]
            if step < self.next_reveal_step:  # type: ignore[attr-defined]
                reject("REPLAYED_MESSAGE", "move step was already revealed")
            if (
                step != self.next_reveal_step  # type: ignore[attr-defined]
                or step >= self.next_step  # type: ignore[attr-defined]
            ):
                reject("OUT_OF_ORDER", "reveal must follow the next locked commitment")
            turn = self._turns[step]  # type: ignore[attr-defined]
            if body["hint"] != turn["hint"]:
                reject("COMMITMENT_MISMATCH", "revealed hint does not match the locked turn")
        except ConformanceError as error:
            remember_error(self._seen, message, error)  # type: ignore[attr-defined]
            raise
        acknowledgement: dict[str, JSONValue] = {
            "profile": PROFILE,
            "version": VERSION,
            "status": "revealed",
            "acknowledges": message["message_id"],
            "game_uid": self.game_uid,  # type: ignore[attr-defined]
            "sub_game_number": self.sub_game_number,  # type: ignore[attr-defined]
            "step": step,
            "move": body["move"],
        }
        self._reveals[step] = body["move"]  # type: ignore[attr-defined]
        self.next_reveal_step += 1  # type: ignore[attr-defined]
        return remember_success(self._seen, message, acknowledgement)  # type: ignore[attr-defined]
