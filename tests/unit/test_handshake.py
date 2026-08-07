"""Unit tests for the simulator-conformant signed-terms handshake."""

import pytest

from p2p_thief_agent.protocol.crypto import CryptoError, canonical_sha256
from p2p_thief_agent.protocol.handshake import (
    Handshake,
    config_sha256,
    identity_block,
    missing_required_terms,
)


def terms() -> dict:
    return {
        "board_size": 7,
        "smell_grid_size": 5,
        "decay_per_step": 0.1,
        "emit_intensity": 0.9,
        "min_center_intensity": 0.9,
        "max_steps": 35,
        "barriers_max": 14,
        "thief_start": [3, 3],
        "cop_start": [0, 0],
    }


def test_config_hash_matches_canonical_and_is_order_independent():
    assert config_sha256(terms()) == canonical_sha256(terms())
    reordered = dict(reversed(list(terms().items())))
    assert config_sha256(reordered) == config_sha256(terms())


def test_missing_required_terms():
    incomplete = terms()
    del incomplete["cop_start"]
    assert missing_required_terms(incomplete) == ["cop_start"]
    assert missing_required_terms(terms()) == []


def test_two_peers_verify_matching_terms():
    alice = Handshake(terms=terms(), identity={"group_id": "alice", "group_name": "alice", "members": ["s1"],
                   "repos": {"cop": "https://x/c", "thief": "https://x/t"},
                   "mcp_servers": {"peer": "https://x/mcp"},
                   "llm_model": "template-free", "spec": {"os": "Windows 11"}})
    bob = Handshake(terms=terms(), identity={"group_id": "bob", "group_name": "bob", "members": ["s1"],
                   "repos": {"cop": "https://x/c", "thief": "https://x/t"},
                   "mcp_servers": {"peer": "https://x/mcp"},
                   "llm_model": "template-free", "spec": {"os": "Windows 11"}})
    alice.verify_peer(bob.signed())
    bob.verify_peer(alice.signed())
    assert alice.peer_identity["group_id"] == "bob"


def test_terms_mismatch_rejected():
    alice = Handshake(terms=terms())
    other = terms()
    other["max_steps"] = 40
    bob = Handshake(terms=other)
    with pytest.raises(CryptoError, match="terms mismatch"):
        alice.verify_peer(bob.signed())


def test_tampered_signature_rejected():
    alice = Handshake(terms=terms())
    message = Handshake(terms=terms()).signed()
    message["signature"] = "f" * 64
    with pytest.raises(CryptoError):
        alice.verify_peer(message)


def test_identity_is_not_covered_by_the_signature():
    """Same terms + a different identity still verifies: identity is not signed.

    That is deliberate — roles alternate across sub-games, so identity is per-group and
    carries no role. The identity must still be *complete* (`M5-014f`), which is a separate
    requirement from being signed: the book mandates its content, and rule 24 charges for an
    incomplete one whether or not a signature covers it.
    """
    alice = Handshake(terms=terms())
    bob = Handshake(terms=terms(), identity={
        "group_id": "bob", "group_name": "Bees", "members": ["b1"],
        "repos": {"cop": "https://x/c", "thief": "https://x/t"},
        "mcp_servers": {"peer": "https://x/mcp"},
        "llm_model": "template-free", "spec": {"os": "Windows 11"}})
    alice.verify_peer(bob.signed())
    assert alice.peer_identity["group_name"] == "Bees"


def test_identity_block_carries_no_role():
    block = identity_block(
        group_id="g", group_name="G", members=[], repos={}, mcp_servers={},
        llm_model="cli-default", spec={},
    )
    assert "role" not in block
    assert block["group_id"] == "g"
