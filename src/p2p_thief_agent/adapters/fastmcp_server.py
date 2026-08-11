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

# Appendix F table 19 sets `queue_depth` to 100 with status **Minimum** — "may be raised by
# agreement but never lowered". Unbounded is not "raised": a mailbox with no ceiling is one
# a flood drives out of memory, and rule 29 (Mandatory) requires DOS detectors precisely
# "to protect network resources".
#
# The reference bounds only its *outbound* gatekeeper and leaves the inbound queues
# unbounded. We bound the inbound side too, because that is the side an opponent controls.
QUEUE_DEPTH_MINIMUM = 100


def _bounded() -> queue.Queue:
    return queue.Queue(maxsize=QUEUE_DEPTH_MINIMUM)


def _enqueue(inbox: queue.Queue, message: object) -> bool:
    """Enqueue without blocking; report refusal rather than waiting.

    `put_nowait`, not `put`: blocking on a full mailbox would hold the MCP request thread
    until the runtime drained it, turning a flood into a hang — and rule 6 makes a freeze
    while awaiting a response a "system deadlock and loss due to timeout". Refusing is
    visible; hanging is not.
    """
    try:
        inbox.put_nowait(message)
    except queue.Full:
        return False
    return True


def _log_call(tool: str, message: object, *, queued: bool) -> None:
    """Record the arrival. Separate function so each tool costs one line, not three."""
    from p2p_thief_agent.services import wire_log  # noqa: PLC0415

    wire_log.received(tool, message, queued=queued)


@dataclass(slots=True)
class PeerInboxes:
    """Thread-safe mailboxes filled by the MCP tools and drained by the runtime.

    Every mailbox is **bounded** (`M8-004b`). A full mailbox refuses rather than growing:
    dropping the oldest would silently discard a turn the opponent believes we received,
    and growing without limit turns a flood into an out-of-memory kill — a technical loss
    scored 0/0 under Table 2.
    """

    agreements: queue.Queue = field(default_factory=_bounded)
    turns: queue.Queue = field(default_factory=_bounded)
    audits: queue.Queue = field(default_factory=_bounded)
    controls: queue.Queue = field(default_factory=_bounded)

    def depths(self) -> dict[str, int]:
        """Current occupancy per mailbox — what an endurance test watches."""
        return {name: getattr(self, name).qsize()
                for name in ("agreements", "turns", "audits", "controls")}


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
        queued = _enqueue(inboxes.agreements, message)
        _log_call("negotiate", message, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        queued = _enqueue(inboxes.turns, message)
        _log_call("receive_turn", message, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        queued = _enqueue(inboxes.audits, payload)
        _log_call("submit_audit", payload, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    @mcp.tool
    def receive_control(message: dict) -> dict:
        queued = _enqueue(inboxes.controls, message)
        _log_call("receive_control", message, queued=queued)
        return {"ok": True} if queued else {"ok": False, "reason": "inbox full"}

    return mcp


def _apply(peer: InboundPeer, tool: str, message: JsonObject) -> Delivery:
    from p2p_thief_agent.services import wire_log  # noqa: PLC0415

    try:
        peer.dispatch(tool, message)
    except (WireError, CryptoError, TypeError) as exc:
        # Recorded here because this is the only place the reason exists: every caller
        # but the turn loop discards the `Delivery`, which is how a refused offer became
        # indistinguishable from silence on 2026-08-11.
        wire_log.validated(tool, accepted=False, reason=exc)
        return Delivery(tool, accepted=False, reason=str(exc))
    wire_log.validated(tool, accepted=True)
    return Delivery(tool, accepted=True)


def _drain_box(box: queue.Queue, peer: InboundPeer, tool: str) -> list[Delivery]:
    """Validate every message queued in one mailbox, in arrival order."""
    results: list[Delivery] = []
    while True:
        try:
            message = box.get_nowait()
        except queue.Empty:
            return results
        results.append(_apply(peer, tool, message))


def drain(inboxes: PeerInboxes, peer: InboundPeer) -> list[Delivery]:
    """Drain every mailbox through the peer, recording accept/reject outcomes."""
    results: list[Delivery] = []
    for tool, box_name in _ROUTES:
        results.extend(_drain_box(getattr(inboxes, box_name), peer, tool))
    return results


def take_turn(inboxes: PeerInboxes, peer: InboundPeer) -> JsonObject | None:
    """Return the opponent's next *accepted* turn, or `None` if none is queued.

    This is the `TakeTurn` source the polling loop drives (`M5-019`). Three
    behaviours here are deliberate:

    * The other three mailboxes are drained first, so a negotiate, audit, or
      control message cannot sit behind the turn we are waiting for. Only a turn
      is returned, because only a turn advances the loop.
    * A rejected turn is **consumed and skipped**, not returned and not left in
      place. The rejection is already a recorded game outcome; leaving it queued
      would make the poller re-reject the same message every interval and starve
      the real turn behind it.
    * Turns are pulled one at a time and the loop **stops at the first accepted
      one**, leaving any later turns queued. A hostile peer can send several at
      once, and draining them all would discard the next step rather than play it.
    """
    for tool, box_name in _ROUTES:
        if box_name != "turns":
            _drain_box(getattr(inboxes, box_name), peer, tool)
    while True:
        try:
            message = inboxes.turns.get_nowait()
        except queue.Empty:
            return None
        if _apply(peer, "receive_turn", message).accepted:
            return message
