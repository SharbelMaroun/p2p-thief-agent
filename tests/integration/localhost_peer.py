"""A standalone Thief peer process for the stage-2 localhost milestone (`M5-002e`).

Run as a script, never imported by the runtime. It exists so a test can start a
**real second OS process** and prove a message crosses a socket between two
independent interpreters, which an in-memory loopback can never show.

Each call is validated through the transport-neutral `InboundPeer` and appended
to a JSONL transcript, giving the test durable evidence of what the second
process actually received. Validation is inline here purely to keep the demo
self-contained; the production runtime keeps enqueue and drain separate so it
controls timing.

    python tests/integration/localhost_peer.py --port 8801 --transcript out.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from fastmcp import FastMCP  # noqa: E402

from p2p_thief_agent.peer import InboundPeer  # noqa: E402
from p2p_thief_agent.protocol.crypto import CryptoError  # noqa: E402
from p2p_thief_agent.protocol.wire import WireError  # noqa: E402


def build(peer: InboundPeer, transcript: Path) -> FastMCP:
    """Return a server that records every call's validation outcome."""
    mcp: FastMCP = FastMCP("p2p-thief-localhost")

    def record(tool: str, argument: dict) -> dict:
        try:
            peer.dispatch(tool, argument)
            entry = {"tool": tool, "accepted": True, "pid": os.getpid()}
        except (WireError, CryptoError, TypeError) as exc:
            entry = {"tool": tool, "accepted": False, "reason": str(exc), "pid": os.getpid()}
        with transcript.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return {"ok": True}

    @mcp.tool
    def negotiate(message: dict) -> dict:
        return record("negotiate", message)

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        return record("receive_turn", message)

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        return record("submit_audit", payload)

    @mcp.tool
    def receive_control(message: dict) -> dict:
        return record("receive_control", message)

    return mcp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    args = parser.parse_args()

    build(InboundPeer(), args.transcript).run(
        transport="http", host="127.0.0.1", port=args.port
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
