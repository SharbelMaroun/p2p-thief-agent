"""Optional-control handler mixin for conformance sessions."""

from __future__ import annotations

from p2p_thief_agent.protocol.canonical import JSONValue
from p2p_thief_agent.protocol.control import validate_control_body
from p2p_thief_agent.protocol.profile import PROFILE, VERSION, ConformanceError, reject
from p2p_thief_agent.protocol.session_support import (
    cached,
    remember_error,
    remember_success,
    validate_envelope,
)


class ControlSessionMixin:
    """Provide capability-gated heartbeat and abort handling."""

    def receive_control(self, value: object, *, now_ms: int) -> dict[str, JSONValue]:
        """Accept an enabled heartbeat or permanently close on abort."""
        message = validate_envelope(
            value,
            "control",
            now_ms,
            maximum_bytes=16_384,
            scan_private=True,
            binding=self._wire_binding(),  # type: ignore[attr-defined]
        )
        try:
            body = validate_control_body(message["body"])
            prior = cached(self._seen, message)  # type: ignore[attr-defined]
            if prior is not None:
                return prior
            if not self.optional_control:  # type: ignore[attr-defined]
                reject(
                    "OPTIONAL_TOOL_UNAVAILABLE",
                    "receive_control was not negotiated",
                )
            control = body["control"]
            if self._closed is not None:  # type: ignore[attr-defined]
                code = (
                    "REPLAYED_MESSAGE"
                    if self._closed == control == "abort"  # type: ignore[attr-defined]
                    else "OUT_OF_ORDER"
                )
                reject(code, "control stream is already closed")
        except ConformanceError as error:
            remember_error(self._seen, message, error)  # type: ignore[attr-defined]
            raise
        acknowledgement: dict[str, JSONValue] = {
            "profile": PROFILE,
            "version": VERSION,
            "status": "accepted",
            "acknowledges": message["message_id"],
            "game_uid": self.game_uid,  # type: ignore[attr-defined]
            "sub_game_number": self.sub_game_number,  # type: ignore[attr-defined]
            "control": control,
        }
        if control == "abort":
            self._closed = "abort"  # type: ignore[attr-defined]
        return remember_success(self._seen, message, acknowledgement)  # type: ignore[attr-defined]
