"""FastMCP server adapter (`M5-002a`).

The Thief runs its own FastMCP server as a public mailbox: each of the four tools
enqueues the opponent's raw message and returns the acknowledgement. With
`fastmcp_client` it is one of only two modules that import `fastmcp`.

**Acknowledgement semantics (`M5-002d`) -- decided and recorded.**
The tools never validate and never raise; `drain` validates afterwards through
`InboundPeer`, and a failure there is a recorded *game outcome*, not a transport
error.

This deliberately diverges from the reference implementation, which validates
structurally inside the tool and lets a malformed message raise so the caller
sees an MCP error. The divergence is kept for one reason: a **tampered audit is
structurally well-formed** yet must be scored as a technical loss under Appendix
E rule 19. A peer that raises invites the opponent to retry it as a transport
fault, and a decided loss then evaporates into a timeout. Being lenient inbound
cannot break an opponent -- it only ever accepts more than required -- whereas
being strict can discard a settled result. The outbound connector is
correspondingly liberal about the shape of an opponent's acknowledgement.
"""

from __future__ import annotations

import queue
from dataclasses import dataclass, field

from fastmcp import FastMCP

from p2p_thief_agent.peer import InboundPeer
from p2p_thief_agent.peer.transport import JsonObject
from p2p_thief_agent.protocol.crypto import CryptoError
from p2p_thief_agent.protocol.wire import WireError


@dataclass(slots=True)
class PeerInboxes:
    """Thread-safe mailboxes filled by the MCP tools and drained by the runtime."""

    agreements: queue.Queue = field(default_factory=queue.Queue)
    turns: queue.Queue = field(default_factory=queue.Queue)
    audits: queue.Queue = field(default_factory=queue.Queue)
    controls: queue.Queue = field(default_factory=queue.Queue)


@dataclass(frozen=True, slots=True)
class Delivery:
    """The outcome of validating one drained message.

    ``accepted`` is ``False`` when this peer rejected the content; ``reason``
    then carries the deterministic error text. A rejection is a game-level
    outcome -- the tool already acknowledged receipt.
    """

    tool: str
    accepted: bool
    reason: str | None = None


# Inbox -> the InboundPeer tool that validates it, in drain order.
_ROUTES = (
    ("negotiate", "agreements"),
    ("receive_turn", "turns"),
    ("submit_audit", "audits"),
    ("receive_control", "controls"),
)


def build_server(inboxes: PeerInboxes, name: str = "p2p-thief") -> FastMCP:
    """Return a FastMCP server whose four tools enqueue and acknowledge."""
    mcp: FastMCP = FastMCP(name)

    @mcp.tool
    def negotiate(message: dict) -> dict:
        inboxes.agreements.put(message)
        return {"ok": True}

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        inboxes.turns.put(message)
        return {"ok": True}

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        inboxes.audits.put(payload)
        return {"ok": True}

    @mcp.tool
    def receive_control(message: dict) -> dict:
        inboxes.controls.put(message)
        return {"ok": True}

    return mcp


def _apply(peer: InboundPeer, tool: str, message: JsonObject) -> Delivery:
    try:
        peer.dispatch(tool, message)
        return Delivery(tool, accepted=True)
    except (WireError, CryptoError, TypeError) as exc:
        return Delivery(tool, accepted=False, reason=str(exc))


def drain(inboxes: PeerInboxes, peer: InboundPeer) -> list[Delivery]:
    """Drain every mailbox through the peer, recording accept/reject outcomes."""
    results: list[Delivery] = []
    for tool, box_name in _ROUTES:
        box: queue.Queue = getattr(inboxes, box_name)
        while True:
            try:
                message = box.get_nowait()
            except queue.Empty:
                break
            results.append(_apply(peer, tool, message))
    return results
