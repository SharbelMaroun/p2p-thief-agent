"""Transport-neutral outbound peer interface (`M5-002c`).

`PeerTransport` is the contract an outbound transport satisfies so the Thief can
reach its opponent without knowing how the bytes travel. The FastMCP connector
implements it; so does any in-memory test double. Nothing here imports FastMCP --
a guard test enforces that (`M5-002b`).

The four methods and their single argument names mirror the adopted wire exactly
(`SIM_WIRE_PROTOCOL.md`): there is **no envelope**, the argument *is* the message
dict. `TOOL_ARGUMENTS` is the single place those names are written down, so the
inbound handler and the outbound connector cannot drift apart -- the failure mode
that a renamed tool would otherwise cause is silent and total.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

JsonObject = dict[str, object]

# Exposed tool -> its single wire argument name. `receive_move` is NOT a tool in
# this profile; it was the withdrawn Option-B name (see `SIM_WIRE_PROTOCOL.md`).
TOOL_ARGUMENTS: dict[str, str] = {
    "negotiate": "message",
    "receive_turn": "message",
    "submit_audit": "payload",
    "receive_control": "message",
}


@runtime_checkable
class PeerTransport(Protocol):
    """The outbound calls a transport exposes to reach the opponent peer."""

    def negotiate(self, message: Mapping[str, object]) -> JsonObject:
        """Send the signed-terms agreement and return the peer's acknowledgement."""
        ...

    def receive_turn(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver one public turn to the opponent and return its acknowledgement."""
        ...

    def submit_audit(self, payload: Mapping[str, object]) -> JsonObject:
        """Deliver the end-of-game audit and return the peer's acknowledgement."""
        ...

    def receive_control(self, message: Mapping[str, object]) -> JsonObject:
        """Deliver an optional control message and return its acknowledgement."""
        ...
