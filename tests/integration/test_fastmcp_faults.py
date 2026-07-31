"""`M5-002g/h/i/b`: how the connector behaves when the opponent misbehaves.

The distinction under test is the one that decides whether a lost game turns
into an endless retry: a peer that cannot be reached (`TransportError`) versus a
peer that answers and refuses (`PeerRejectionError`).
"""

from pathlib import Path

import pytest
from fastmcp import FastMCP

from p2p_thief_agent.adapters import (
    FastMCPClient,
    PeerInboxes,
    PeerRejectionError,
    TransportError,
    build_server,
)

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent"
TURN = {"step": 1, "sender": "police", "hint": "near the park", "smell_grid": {"3,3": 0.9},
        "commit": "a" * 64, "timestamp": "t"}


def _peer_returning(value: object) -> FastMCP:
    """A one-tool FastMCP server whose `receive_turn` returns exactly ``value``."""
    mcp: FastMCP = FastMCP("scripted-peer")

    @mcp.tool
    def receive_turn(message: dict) -> object:
        return value

    return mcp


def test_an_unreachable_opponent_raises_a_transport_error() -> None:
    with pytest.raises(TransportError):
        FastMCPClient("http://127.0.0.1:1/mcp", timeout=5.0).receive_turn(TURN)


def test_a_reply_that_is_not_a_json_object_is_a_transport_error() -> None:
    with pytest.raises(TransportError):
        FastMCPClient(_peer_returning("not-an-object")).receive_turn(TURN)


@pytest.mark.parametrize(
    "ack", [{"ok": True}, {"status": "ok"}, {"status": "delivered"}, {"ok": True, "x": 1}]
)
def test_any_non_refusing_json_object_counts_as_an_acknowledgement(ack: dict) -> None:
    """The opponent's ack shape is not fixed by the profile, so accept broadly.

    This peer sends ``{"ok": true}``, but the reference implementation's exact
    dict is not established. Demanding our own shape would read every successful
    delivery from such a peer as a refusal and abandon a healthy game.
    """
    assert FastMCPClient(_peer_returning(ack)).receive_turn(TURN) == ack


@pytest.mark.parametrize(
    "refusal", [{"ok": False}, {"status": "rejected"}, {"error": "illegal move"}]
)
def test_an_explicit_refusal_is_a_rejection_not_a_transport_error(refusal: dict) -> None:
    with pytest.raises(PeerRejectionError) as caught:
        FastMCPClient(_peer_returning(refusal)).receive_turn(TURN)
    assert not isinstance(caught.value, TransportError)


def test_neither_failure_type_inherits_the_other() -> None:
    """So `except TransportError` can never swallow a decided game outcome."""
    assert not issubclass(PeerRejectionError, TransportError)
    assert not issubclass(TransportError, PeerRejectionError)


def test_the_client_keeps_no_session_state_between_calls() -> None:
    """__slots__ makes hidden per-turn state impossible, not merely absent."""
    inboxes = PeerInboxes()
    client = FastMCPClient(build_server(inboxes))
    client.receive_turn(TURN)
    client.receive_turn(TURN | {"step": 2})
    assert not hasattr(client, "__dict__")
    assert set(FastMCPClient.__slots__) == {"_target", "_timeout"}
    assert inboxes.turns.qsize() == 2


def test_only_the_adapters_package_imports_fastmcp() -> None:
    offenders = [
        path.relative_to(SRC)
        for path in SRC.rglob("*.py")
        if path.parent.name != "adapters"
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().lower().startswith(("import fastmcp", "from fastmcp"))
    ]
    assert offenders == []
