"""FastMCP client connector (`M5-002c`).

The outbound half of the peer boundary: implements `peer.PeerTransport` over
FastMCP so the runtime can reach an opponent without knowing the carrier. With
`fastmcp_server` it is one of only two modules that import `fastmcp`.

**Two failure kinds, deliberately separate.** `TransportError` means the exchange
itself failed -- unreachable host, timeout, or a reply that is not a JSON object
-- so the caller may retry or declare a technical loss. `PeerRejectionError`
means the opponent was reached, answered, and refused; that is a game outcome and
retrying it is wrong. Collapsing the two would make a peer that legitimately
refuses look like a flaky network, which is exactly what Appendix E rules 6/7
forbid.

**Liberal about the acknowledgement shape (`M5-002h`).** This peer sends
`{"ok": true}`, but the profile never fixed what an opponent must send back and
the reference implementation's exact ack dict is not established -- it may be
`{"status": "ok"}` or `{"status": "delivered"}`. Demanding our own shape would
read every successful delivery from such a peer as a refusal and abandon a
healthy game, so any JSON object is accepted unless it explicitly signals
failure.

**Stateless by construction (`M5-002i`).** Every call opens and closes its own
session and `__slots__` leaves nowhere for per-turn state to hide.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping

from fastmcp import Client

from p2p_thief_agent.peer.transport import TOOL_ARGUMENTS, JsonObject

# Values of a ``status`` field by which an opponent signals refusal.
_REFUSAL_WORDS = frozenset({"error", "failed", "failure", "rejected", "refused", "denied"})


class TransportError(RuntimeError):
    """The opponent could not be reached, or did not answer with a JSON object."""


class PeerRejectionError(RuntimeError):
    """The opponent answered but declined the message: a game-level outcome."""


def signals_refusal(response: Mapping[str, object]) -> bool:
    """Return whether a well-formed reply explicitly says the peer refused.

    Silence is not refusal: only an explicit ``ok: false``, a ``status`` naming a
    failure, or a non-empty ``error`` member counts.
    """
    if response.get("ok") is False:
        return True
    status = response.get("status")
    if isinstance(status, str) and status.strip().lower() in _REFUSAL_WORDS:
        return True
    return response.get("error") not in (None, "")


class FastMCPClient:
    """Outbound `PeerTransport` over FastMCP.

    ``target`` is whatever `fastmcp.Client` accepts: an opponent URL in
    production, or an in-memory `FastMCP` server in tests. The URL comes from
    private configuration only, never from the shared agreed terms (`ADR-0004`);
    this class receives it and reads no configuration itself, so it has no path
    to the shared object at all.
    """

    __slots__ = ("_target", "_timeout")

    def __init__(self, target: object, *, timeout: float | None = None) -> None:
        self._target = target
        self._timeout = timeout

    def negotiate(self, message: Mapping[str, object]) -> JsonObject:
        """Send the signed-terms agreement and return the peer's acknowledgement."""
        return self.call("negotiate", message)

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver one public turn to the opponent and return its acknowledgement."""
        return self.call("receive_turn", message)

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        """Deliver the end-of-game audit and return the peer's acknowledgement."""
        return self.call("submit_audit", payload)

    def receive_control(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver an optional control message and return its acknowledgement."""
        return self.call("receive_control", message)

    def call(self, tool: str, argument: Mapping[str, object]) -> JsonObject:
        """Invoke one exposed tool, shaping its single wire argument.

        ``submit_audit`` takes ``payload``; the other three take ``message``. The
        names come from `TOOL_ARGUMENTS`, so the inbound and outbound halves
        cannot drift apart.
        """
        keyword = TOOL_ARGUMENTS.get(tool)
        if keyword is None:
            raise TransportError(f"unknown tool {tool!r}")
        return self._unwrap(tool, self._exchange(tool, {keyword: dict(argument)}))

    def _exchange(self, tool: str, arguments: JsonObject) -> object:
        """Run one request/response, mapping every carrier failure to one type."""
        try:
            return asyncio.run(self._invoke(tool, arguments))
        except Exception as exc:  # noqa: BLE001 - any carrier failure is one fault
            raise TransportError(f"{tool} failed in transport: {exc}") from exc

    async def _invoke(self, tool: str, arguments: JsonObject) -> object:
        """Open a session, call the tool, and close it again."""
        request = self._request(tool, arguments)
        if self._timeout is None:
            return await request
        return await asyncio.wait_for(request, self._timeout)

    async def _request(self, tool: str, arguments: JsonObject) -> object:
        async with Client(self._target) as client:
            return await client.call_tool(tool, arguments)

    @staticmethod
    def _unwrap(tool: str, result: object) -> JsonObject:
        """Return the peer's acknowledgement, or raise the right failure kind."""
        data = getattr(result, "data", None)
        if not isinstance(data, Mapping):
            raise TransportError(f"{tool} returned no JSON object: {data!r}")
        response: JsonObject = dict(data)
        if signals_refusal(response):
            raise PeerRejectionError(f"{tool} was declined by the opponent: {response}")
        return response
