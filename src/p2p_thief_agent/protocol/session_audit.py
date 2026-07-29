"""Final-audit handler mixin for conformance sessions."""

from __future__ import annotations

from p2p_thief_agent.protocol.audit import verify_audit_records
from p2p_thief_agent.protocol.canonical import JSONValue
from p2p_thief_agent.protocol.profile import (
    PROFILE,
    VERSION,
    ConformanceError,
    reject,
    require_closed,
)
from p2p_thief_agent.protocol.session_support import (
    cached,
    remember_error,
    remember_success,
    validate_envelope,
)


class AuditSessionMixin:
    """Provide exact final-reveal verification and terminal outcomes."""

    def submit_audit(self, value: object, *, now_ms: int) -> dict[str, JSONValue]:
        """Verify one complete, ordered final audit against locked turns."""
        message = validate_envelope(
            value,
            "final_audit",
            now_ms,
            maximum_bytes=8_388_608,
            scan_private=False,
            binding=self._wire_binding(),  # type: ignore[attr-defined]
        )
        try:
            body = require_closed(message["body"], ("records",), "body")
            records = body["records"]
            if not isinstance(records, list):
                reject("MALFORMED", "body.records must be an array")
            prior = cached(self._seen, message)  # type: ignore[attr-defined]
            if prior is not None:
                return prior
            if self._closed == "audited":  # type: ignore[attr-defined]
                reject("REPLAYED_MESSAGE", "final audit was already accepted")
            if self._closed is not None:  # type: ignore[attr-defined]
                reject("OUT_OF_ORDER", "audit stream is already closed")
            if self.next_reveal_step != self.next_step:  # type: ignore[attr-defined]
                reject("OUT_OF_ORDER", "every locked turn must be live-revealed first")
            if len(records) != len(self._turns):  # type: ignore[attr-defined]
                reject(
                    "OUT_OF_ORDER",
                    "audit must contain exactly one record per locked turn",
                )
            digest = verify_audit_records(
                game_id=self.game_id,  # type: ignore[attr-defined]
                game_uid=self.game_uid,  # type: ignore[attr-defined]
                sub_game_number=self.sub_game_number,  # type: ignore[attr-defined]
                sender_group_id=self.remote_group_id,  # type: ignore[attr-defined]
                next_step=self.next_step,  # type: ignore[attr-defined]
                turns=self._turns,  # type: ignore[attr-defined]
                reveals=self._reveals,  # type: ignore[attr-defined]
                records=records,
                board_size=self.board_size,  # type: ignore[attr-defined]
            )
        except ConformanceError as error:
            if error.code == "COMMITMENT_MISMATCH":
                self.technical_loss = True  # type: ignore[attr-defined]
                self.score = 0  # type: ignore[attr-defined]
                self._closed = "technical_loss"  # type: ignore[attr-defined]
            remember_error(self._seen, message, error)  # type: ignore[attr-defined]
            raise
        acknowledgement: dict[str, JSONValue] = {
            "profile": PROFILE,
            "version": VERSION,
            "status": "verified",
            "acknowledges": message["message_id"],
            "game_uid": self.game_uid,  # type: ignore[attr-defined]
            "sub_game_number": self.sub_game_number,  # type: ignore[attr-defined]
            "record_count": len(records),
            "audit_sha256": digest,
        }
        self._closed = "audited"  # type: ignore[attr-defined]
        return remember_success(self._seen, message, acknowledgement)  # type: ignore[attr-defined]
