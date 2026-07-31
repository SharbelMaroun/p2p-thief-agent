"""`M5-014`: the live handler really refuses, not just the policy module.

`test_agreement.py` proves the policy in isolation. What matters at run time is
that the inbound handler actually applies it once the runtime has loaded this
peer's own terms -- and that it still only shape-checks before then, which is the
state a peer is in while it is still starting up.
"""

import pytest

from p2p_thief_agent.peer.inbound import InboundPeer
from p2p_thief_agent.protocol.crypto import commit_of
from p2p_thief_agent.protocol.wire import WireError

NONCE = "0123456789abcdef0123456789abcdef"

TERMS = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.10, "emit_intensity": 0.9,
    "min_center_intensity": 0.05, "max_steps": 35, "barriers_max": 14,
    "setting": "New York", "hint_max_words": 15, "axis_origin_corner": "top-left",
    "axis_start_index": 0, "thief_start": [3, 3], "cop_start": [0, 0], "num_games": 6,
}
IDENTITY = {"identity": {"group_id": "cop-team"}}


def offer(**changes: object) -> dict:
    terms = {**TERMS, **changes}
    return {"terms": terms, "nonce": NONCE, "signature": commit_of(terms, NONCE), **IDENTITY}


def test_a_matching_offer_is_agreed_and_remembered() -> None:
    peer = InboundPeer(my_terms=TERMS)
    assert peer.negotiate(offer()) == {"ok": True}
    assert peer.agreed_terms == TERMS
    assert peer.opponent_group == "cop-team"


def test_a_mismatched_offer_is_refused_by_name_and_agrees_nothing() -> None:
    peer = InboundPeer(my_terms={**TERMS, "hint_max_words": 20})
    with pytest.raises(WireError, match="hint_max_words"):
        peer.negotiate(offer())
    assert peer.agreed_terms is None


def test_a_below_minimum_offer_is_refused_by_the_live_handler() -> None:
    peer = InboundPeer(my_terms=TERMS)
    with pytest.raises(WireError, match="board_size is a MINIMUM"):
        peer.negotiate(offer(board_size=5))


def test_a_forged_signature_is_refused_by_the_live_handler() -> None:
    peer = InboundPeer(my_terms=TERMS)
    message = offer()
    message["terms"]["barriers_max"] = 99
    with pytest.raises(WireError, match="signature"):
        peer.negotiate(message)


def test_without_its_own_terms_the_handler_only_checks_the_shape() -> None:
    """Before the shared match object is loaded there is nothing to compare to."""
    peer = InboundPeer()
    assert peer.negotiate(offer(board_size=5)) == {"ok": True}
    assert peer.agreed_terms is None
    assert peer.opponent_group == "cop-team"


def test_a_structurally_incomplete_offer_is_refused_either_way() -> None:
    for peer in (InboundPeer(), InboundPeer(my_terms=TERMS)):
        message = offer()
        del message["signature"]
        with pytest.raises(WireError, match="signature"):
            peer.negotiate(message)
