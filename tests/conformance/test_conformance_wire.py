"""`M1-016`: our real client against the neutral peer, over an actual FastMCP wire.

`test_conformance.py` proves the *rules* agree by calling the stub in Python.
This file proves the *call shapes* agree by driving `FastMCPClient` — the same class
production uses — against the stub behind a real MCP server.

The distinction is not academic. If our client calls `submit_audit` and a peer registered
that tool under another name, every rule in the project can be correct and the two agents
still never exchange a message. The rules-level suite would stay green throughout,
because it never uses a tool name. Only this file can fail on it.

Neither the tool names nor the argument names are imported from our adapters here; they
are written out by hand from `docs/SIM_WIRE_PROTOCOL.md`, so agreement means two
independent readings of the profile rather than one constant agreeing with itself.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.adapters import FastMCPClient, TransportError
from p2p_thief_agent.protocol.crypto import commit_of, new_nonce, seal
from tests.conformance.neutral_peer import NeutralPeer
from tests.conformance.neutral_peer_server import build_neutral_server
from tests.conformance.test_conformance import TERMS

EXPECTED_WIRE = {
    "negotiate": "message",
    "receive_turn": "message",
    "submit_audit": "payload",
    "receive_control": "message",
}


@pytest.fixture
def wired() -> tuple[FastMCPClient, NeutralPeer]:
    peer = NeutralPeer(dict(TERMS))
    return FastMCPClient(build_neutral_server(peer)), peer


def _offer() -> dict:
    nonce = new_nonce()
    return {
        "identity": {"group_id": "sharbel-thief"},
        "terms": TERMS,
        "nonce": nonce,
        "signature": commit_of(TERMS, nonce),
    }


def _discover(peer: NeutralPeer) -> dict[str, dict]:
    """List the tools the way a stranger would: over the wire, via a plain MCP client.

    Deliberately not `server.list_tools()` — a stranger has no handle on our server
    object, only the endpoint. Discovery is the first thing that happens in a real match.
    """
    import asyncio

    from fastmcp import Client

    async def run() -> dict[str, dict]:
        async with Client(build_neutral_server(peer)) as client:
            return {t.name: (t.inputSchema or {}) for t in await client.list_tools()}

    return asyncio.run(run())


def test_the_wire_advertises_exactly_the_four_tools(wired) -> None:
    """A name a stranger cannot guess is a match that never starts."""
    _, peer = wired
    assert set(_discover(peer)) == set(EXPECTED_WIRE)


def test_each_tool_takes_exactly_the_expected_argument_name(wired) -> None:
    """`submit_audit` takes `payload`; the other three take `message`. A mismatch here
    fails at the transport, before any game rule is ever consulted."""
    _, peer = wired
    discovered = _discover(peer)
    for name, argument in EXPECTED_WIRE.items():
        properties = discovered[name].get("properties", {})
        assert argument in properties, f"{name} does not take {argument!r}, got {list(properties)}"


def test_our_offer_crosses_the_wire_and_is_accepted(wired) -> None:
    client, _ = wired
    reply = client.negotiate(_offer())
    assert reply["terms"] == TERMS


def test_our_sealed_turn_crosses_the_wire(wired) -> None:
    client, peer = wired
    sealed = seal({"step": 1, "move": "N"})
    reply = client.receive_turn({
        "step": 1, "sender": "sharbel-thief", "hint": "near the north edge",
        "smell_grid": {"0,0": 0.9}, "commit": sealed["commit"],
        "timestamp": "2026-08-06T00:00:00Z",
    })
    assert reply["status"] == "received"
    assert peer.turns[0]["step"] == 1


def test_our_audit_reproduces_under_the_stubs_own_hashing(wired) -> None:
    """The audit is where a canonicalization drift becomes a technical loss (rule 19)."""
    client, _ = wired
    sealed = seal({"step": 1, "move": "N", "hint": "café near the north edge"})
    reply = client.submit_audit({
        "sender": "sharbel-thief", "result_claim": "survival",
        "records": [{"payload": {"step": 1, "move": "N", "hint": "café near the north edge"},
                     "nonce": sealed["nonce"], "commit": sealed["commit"]}],
    })
    assert reply["records"] == 1


def test_a_control_message_crosses_the_wire(wired) -> None:
    client, peer = wired
    assert client.receive_control({"kind": "ping", "sender": "sharbel-thief"})["status"] == "received"
    assert peer.controls[0]["kind"] == "ping"


def test_a_refusal_reaches_us_as_a_transport_error_not_a_silent_success(wired) -> None:
    """The reference raises rather than acking and dropping, so our client must *see* the
    refusal. A peer that swallowed it would leave us waiting on a turn that never comes —
    which is a timeout, and a timeout is a technical loss."""
    client, _ = wired
    with pytest.raises(TransportError):
        client.receive_turn({"step": 1, "sender": "x"})  # missing required fields


def test_a_tampered_audit_record_is_refused_across_the_wire(wired) -> None:
    """Rule 19, Mandatory, iron rule: score 0 for the falsifying group."""
    client, _ = wired
    sealed = seal({"step": 1, "move": "N"})
    with pytest.raises(TransportError):
        client.submit_audit({
            "sender": "x", "result_claim": "survival",
            "records": [{"payload": {"step": 1, "move": "S"},  # move changed after sealing
                         "nonce": sealed["nonce"], "commit": sealed["commit"]}],
        })


def test_private_state_is_refused_across_the_wire(wired) -> None:
    """Rule 2, Prohibited: immediate disqualification due to data leakage."""
    client, _ = wired
    sealed = seal({"step": 1, "move": "N"})
    with pytest.raises(TransportError):
        client.receive_turn({
            "step": 1, "sender": "x", "hint": "h", "smell_grid": {}, "commit": sealed["commit"],
            "timestamp": "2026-08-06T00:00:00Z", "belief": {"0,0": 0.9},
        })
