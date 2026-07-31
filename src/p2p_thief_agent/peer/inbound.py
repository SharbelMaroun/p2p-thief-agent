"""Transport-neutral inbound peer handler (`M5-002`).

Turns the four exposed tool calls into protocol-layer actions with no transport
code: the FastMCP server adapter wraps it, but every validation lives in
`protocol/` where it can be tested without a socket (`PS-007`).

Each handler either returns the acknowledgement or raises `WireError`/`CryptoError`,
which the adapter records as a **game-level outcome** rather than a transport
failure. That distinction is the whole point: a tampered audit is structurally
well-formed and must be *scored* as a technical loss under Appendix E rule 19, so
it must never be thrown away as a network error.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from p2p_thief_agent.peer.transport import JsonObject
from p2p_thief_agent.protocol.agreement import AgreementError, accept_offer
from p2p_thief_agent.protocol.crypto import audit_records
from p2p_thief_agent.protocol.wire import AuditPayload, ControlMessage, TurnMessage, WireError

# What this peer sends back on success. The profile does not fix the opponent's
# shape, so the outbound connector stays liberal about what it accepts.
OK_RESPONSE: JsonObject = {"ok": True}


class InboundPeer:
    """Validate inbound tool calls for one sub-game, holding no transport state."""

    __slots__ = ("_dispatch", "agreed_terms", "audits_verified", "my_terms", "opponent_group", "turns")

    def __init__(self, my_terms: Mapping[str, object] | None = None) -> None:
        self.turns: list[TurnMessage] = []
        self.opponent_group: str | None = None
        self.audits_verified: list[dict] = []
        # This peer's own agreed terms. Supplied once the runtime has loaded the
        # shared match object; until then `negotiate` can only check the shape.
        self.my_terms: Mapping[str, object] | None = my_terms
        self.agreed_terms: dict | None = None
        self._dispatch: dict[str, Callable[[Mapping[str, object]], JsonObject]] = {
            "negotiate": self.negotiate,
            "receive_turn": self.receive_turn,
            "submit_audit": self.submit_audit,
            "receive_control": self.receive_control,
        }

    def negotiate(self, message: Mapping[str, object]) -> JsonObject:
        """Decide whether this peer will play, and record the opponent's identity.

        When the runtime has supplied `my_terms`, this is the real Appendix E rule
        11 gate: signature, Appendix F, and every term compared against our own,
        refusing by name. Without them only the wire shape can be checked, which is
        the state before the shared match object is loaded (`M5-014`).
        """
        for field in ("terms", "nonce", "signature"):
            if field not in message:
                raise WireError(f"negotiate missing field: {field!r}")
        identity = message.get("identity")
        if identity is not None and not isinstance(identity, Mapping):
            raise WireError("negotiate identity must be an object")
        if self.my_terms is not None:
            try:
                self.agreed_terms = accept_offer(message, self.my_terms)
            except AgreementError as exc:
                raise WireError(f"negotiate refused: {exc}") from exc
        self.opponent_group = (identity or {}).get("group_id")
        return dict(OK_RESPONSE)

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        """Admit one public turn, rejecting a malformed or replayed step."""
        turn = TurnMessage.from_dict(dict(message))
        if any(seen.step == turn.step and seen.sender == turn.sender for seen in self.turns):
            raise WireError(f"replayed turn for step {turn.step} from {turn.sender!r}")
        self.turns.append(turn)
        return dict(OK_RESPONSE)

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        """Accept an end-of-game audit only if every commitment reproduces.

        A mismatch is an automatic zero for the falsifying peer (Appendix E rule
        19), so this raises rather than silently accepting; the caller records it
        as a decided outcome.
        """
        audit = AuditPayload.from_dict(dict(payload))
        report = audit_records(audit.records)
        if not report["passed"]:
            raise WireError(f"audit failed for steps {report['failed_steps']}")
        self.audits_verified.append(report)
        return dict(OK_RESPONSE)

    def receive_control(self, message: Mapping[str, object]) -> JsonObject:
        """Validate an optional control-channel signal."""
        ControlMessage.from_dict(dict(message))
        return dict(OK_RESPONSE)

    def dispatch(self, tool_name: str, argument: Mapping[str, object]) -> JsonObject:
        """Route one inbound tool call to its handler, rejecting unknown tools."""
        handler = self._dispatch.get(tool_name)
        if handler is None:
            raise WireError(f"unknown tool {tool_name!r}")
        return handler(argument)
