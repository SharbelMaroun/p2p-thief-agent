"""Expose the neutral peer over a real FastMCP wire (`M1-016`).

`test_conformance.py` calls :class:`NeutralPeer` directly, which proves the **rules**
agree. This module puts the same peer behind an actual MCP server so the **call shapes**
are proven too: the tool names a stranger must call and the argument name each one takes.

That is a different failure mode, and the one that ends a match before it starts. If our
client calls `submit_audit` and a peer registered `exchange_audit`, every rule in the
project can be right and the two agents still never speak. Only a wire test catches it —
the rules-level test above would pass regardless, because it never uses the names.

The tool names here are written out **by hand** from `docs/SIM_WIRE_PROTOCOL.md` rather
than imported from `p2p_thief_agent.adapters`, for the same reason the crypto is
re-derived: importing our own constant would make the test agree with itself.
"""

from __future__ import annotations

from fastmcp import FastMCP

from tests.conformance.neutral_peer import ConformanceError, NeutralPeer


def build_neutral_server(peer: NeutralPeer, name: str = "neutral-stub") -> FastMCP:
    """Register exactly the four tools, with exactly the four argument names.

    Handlers **raise** on invalid input rather than acknowledging and dropping it, which
    is what the reference does: its tool handlers construct protocol dataclasses that
    raise on a missing or mistyped field, and FastMCP returns that to the sender as an
    MCP error. A stub that acked everything would prove nothing about refusal.
    """
    server = FastMCP(name)

    @server.tool()
    def negotiate(message: dict) -> dict:
        return peer.negotiate(message)

    @server.tool()
    def receive_turn(message: dict) -> dict:
        return peer.receive_turn(message)

    @server.tool()
    def submit_audit(payload: dict) -> dict:
        return peer.submit_audit(payload)

    @server.tool()
    def receive_control(message: dict) -> dict:
        return peer.receive_control(message)

    return server


__all__ = ["ConformanceError", "NeutralPeer", "build_neutral_server"]
