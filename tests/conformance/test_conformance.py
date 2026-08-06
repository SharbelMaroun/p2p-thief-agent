"""`M1-016`: our protocol layer proven against a peer sharing none of its code.

The stub in `neutral_peer.py` imports nothing from `p2p_thief_agent` and re-derives
canonicalization and the commit construction from the profile document. So when our
sealed message verifies over there, two implementations agree — unlike a test that drives
our client against our server, where a typo in a shared constant cancels out on both
sides and the suite stays green.

Proven by injection rather than asserted: changing the commit separator in
`protocol/crypto.py` from `|` to `:` — a one-character drift — fails four tests here and
none elsewhere in the suite.

`test_negative_vectors.py` carries the `M1-017` half.
"""


from __future__ import annotations

from p2p_thief_agent.protocol.crypto import commit_of, new_nonce, seal
from tests.conformance.neutral_peer import TOOLS, NeutralPeer

TERMS = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.1, "emit_intensity": 0.9,
    "max_steps": 35, "barriers_max": 14, "thief_start": [0, 0], "cop_start": [6, 6],
}


def _peer(**kw) -> NeutralPeer:
    return NeutralPeer(dict(TERMS), **kw)


def _offer(terms: dict | None = None) -> dict:
    """Build the negotiate message our side sends, using **our** crypto."""
    used = TERMS if terms is None else terms
    nonce = new_nonce()
    return {
        "identity": {"group_id": "sharbel-thief"},
        "terms": used,
        "nonce": nonce,
        "signature": commit_of(used, nonce),
    }


def _turn(step: int = 1, **extra) -> dict:
    sealed = seal({"step": step, "move": "N"})
    message = {
        "step": step, "sender": "sharbel-thief", "hint": "near the north edge",
        "smell_grid": {"0,0": 0.9}, "commit": sealed["commit"],
        "timestamp": "2026-08-06T00:00:00Z",
    }
    message.update(extra)
    return message


# --- M1-016: bidirectional, two identities, no profile edit -------------------------


def test_the_four_tool_names_and_argument_names_are_exact() -> None:
    """A wrong tool or argument name means a classmate simply cannot call us."""
    assert TOOLS == {
        "negotiate": "message", "receive_turn": "message",
        "submit_audit": "payload", "receive_control": "message",
    }


def test_our_offer_is_accepted_by_a_peer_that_shares_no_code_with_us() -> None:
    """Thief-proposes: our signature reproduces under the stub's own hashing."""
    reply = _peer().negotiate(_offer())
    assert reply["terms"] == TERMS


def test_we_accept_the_stubs_counter_offer() -> None:
    """Thief-accepts. Both directions must pass without editing a profile file."""
    reply = _peer().negotiate(_offer())
    assert commit_of(reply["terms"], reply["nonce"]) == reply["signature"]


def test_two_different_participant_identities_change_no_agreed_byte() -> None:
    """Identity carries no role and is not signed, so swapping it must not move the hash."""
    first, second = _offer(), _offer()
    second["identity"] = {"group_id": "someone-else-entirely"}
    second["nonce"], second["signature"] = first["nonce"], first["signature"]
    assert _peer().negotiate(first)["config_sha256"] == _peer().negotiate(second)["config_sha256"]


def test_a_sealed_turn_and_audit_cross_to_the_stub_and_reproduce() -> None:
    sealed = seal({"step": 1, "move": "N"})
    peer = _peer()
    assert peer.receive_turn(_turn(1, commit=sealed["commit"])) == {"status": "received"}
    audit = {
        "sender": "sharbel-thief", "result_claim": "survival",
        "records": [{"payload": {"step": 1, "move": "N"},
                     "nonce": sealed["nonce"], "commit": sealed["commit"]}],
    }
    assert peer.submit_audit(audit)["records"] == 1
