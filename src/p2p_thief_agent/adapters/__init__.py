"""Transport adapters (`M5-002`).

Importing from this package pulls in transport dependencies (`fastmcp`). The
transport-neutral core (`p2p_thief_agent.peer`, `.protocol`, `.sdk`) never
imports it, and a guard test enforces that boundary (`M5-002b`).
"""

from p2p_thief_agent.adapters.fastmcp_client import (
    FastMCPClient,
    PeerRejectionError,
    TransportError,
    signals_refusal,
)
from p2p_thief_agent.adapters.fastmcp_server import (
    Delivery,
    PeerInboxes,
    build_server,
    drain,
)

__all__ = [
    "Delivery",
    "FastMCPClient",
    "PeerInboxes",
    "PeerRejectionError",
    "TransportError",
    "build_server",
    "drain",
    "signals_refusal",
]
