"""`M5-002`: the Thief runs as both FastMCP server and client.

Tool surface, argument shaping, and the acknowledgement semantics decided in
`M5-002d`. Fault handling lives in `test_fastmcp_faults.py`.

Driven against an in-memory `build_server`, so no process, port, or tunnel is
involved.
"""

import pytest

from p2p_thief_agent.adapters import (
    FastMCPClient,
    PeerInboxes,
    TransportError,
    build_server,
    drain,
)
from p2p_thief_agent.peer import InboundPeer, PeerTransport
from p2p_thief_agent.protocol.crypto import seal

TURN = {"step": 1, "sender": "police", "hint": "near the park", "smell_grid": {"3,3": 0.9},
        "commit": "a" * 64, "timestamp": "t"}
AGREEMENT = {"terms": {"board_size": 7}, "nonce": "0" * 32, "signature": "b" * 64,
             "identity": {"group_id": "group-beta"}}
CONTROL = {"kind": "status", "sender": "police"}


def audit(tamper: bool = False) -> dict:
    """Build a real sealed audit; ``tamper`` mutates the payload after sealing."""
    payload = {"step": 1, "move": "MOVE:N"}
    sealed = seal(payload)
    record = {"payload": payload, "nonce": sealed["nonce"], "commit": sealed["commit"]}
    if tamper:
        record["payload"] = {"step": 1, "move": "MOVE:S"}
    return {"sender": "police", "records": [record], "result_claim": "survival"}


def test_client_satisfies_the_transport_port() -> None:
    assert isinstance(FastMCPClient(build_server(PeerInboxes())), PeerTransport)


def test_each_tool_delivers_to_its_own_inbox_with_the_right_argument_name() -> None:
    """Arrival proves the shape: a wrong argument name would fail the call.

    ``submit_audit`` takes ``payload``; the other three take ``message``.
    """
    inboxes = PeerInboxes()
    client = FastMCPClient(build_server(inboxes))

    assert client.negotiate(AGREEMENT) == {"ok": True}
    assert client.receive_turn(TURN) == {"ok": True}
    assert client.submit_audit(audit()) == {"ok": True}
    assert client.receive_control(CONTROL) == {"ok": True}

    assert inboxes.agreements.get_nowait()["nonce"] == "0" * 32
    assert inboxes.turns.get_nowait()["step"] == 1
    assert inboxes.audits.get_nowait()["result_claim"] == "survival"
    assert inboxes.controls.get_nowait()["kind"] == "status"


def test_receive_move_is_not_exposed() -> None:
    """The withdrawn Option-B name must not reappear: it would be unreachable."""
    with pytest.raises(TransportError, match="unknown tool"):
        FastMCPClient(build_server(PeerInboxes())).call("receive_move", TURN)


def test_a_full_round_trip_validates_on_drain_not_at_call_time() -> None:
    inboxes = PeerInboxes()
    client = FastMCPClient(build_server(inboxes))
    client.negotiate(AGREEMENT)
    client.receive_turn(TURN)
    client.receive_control(CONTROL)
    client.submit_audit(audit())

    peer = InboundPeer()
    assert [(d.tool, d.accepted) for d in drain(inboxes, peer)] == [
        ("negotiate", True), ("receive_turn", True),
        ("submit_audit", True), ("receive_control", True),
    ]
    assert peer.opponent_group == "group-beta"


def test_malformed_content_is_acknowledged_then_rejected_on_drain() -> None:
    """The tool acks anything; the rejection is a game outcome, not a fault."""
    inboxes = PeerInboxes()
    assert FastMCPClient(build_server(inboxes)).receive_turn({"bad": "turn"}) == {"ok": True}
    results = drain(inboxes, InboundPeer())
    assert (results[0].tool, results[0].accepted) == ("receive_turn", False)
    assert results[0].reason is not None


def test_a_tampered_audit_is_received_and_scored_not_lost_as_a_fault() -> None:
    """Rule 19 makes this a technical loss, so it must survive transport to be scored.

    This is the reason the tools never raise: a peer that rejected it at call
    time would invite the opponent to retry a decided loss as a network blip.
    """
    inboxes = PeerInboxes()
    FastMCPClient(build_server(inboxes)).submit_audit(audit(tamper=True))
    results = drain(inboxes, InboundPeer())
    assert (results[0].tool, results[0].accepted) == ("submit_audit", False)
    assert "audit failed" in (results[0].reason or "")


def test_a_replayed_turn_is_rejected_deterministically() -> None:
    peer = InboundPeer()
    peer.receive_turn(TURN)
    with pytest.raises(Exception, match="replayed turn"):
        peer.receive_turn(TURN)
