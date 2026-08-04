"""`M6-005`/`M5-015`: lock, exchange, and verify the scent model at negotiation (`AE-23`).

The lock rides in the agreed terms, so the ordinary agreement gate compares it and refuses
a mismatch by name — a deviation cancels the game before the first move.
"""

import pytest

from p2p_thief_agent.orchestration.negotiation import NegotiationError, negotiate_match
from p2p_thief_agent.perception.scent_lock import (
    SCENT_MODEL_TERM,
    scent_model_hash,
    scent_model_record,
    with_scent_lock,
)
from p2p_thief_agent.protocol.agreement import AgreementError, accept_offer
from p2p_thief_agent.protocol.crypto import canonical_sha256
from p2p_thief_agent.protocol.handshake import Handshake

TERMS = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.10, "emit_intensity": 0.9,
    "max_steps": 35, "barriers_max": 14, "thief_start": [0, 0], "cop_start": [6, 6],
    "num_games": 6,
}


def test_the_record_carries_the_formula_constants_field_and_profile() -> None:
    """`M6-005a`: one canonical record, hashable to a stable lock."""
    record = scent_model_record()
    assert record["decay_per_step"] == 0.10
    assert record["center_intensity"] == 0.9
    assert record["field_size"] == 5
    assert record["emission_profile_by_squared_distance"]["0"] == 0.90
    assert scent_model_hash() == scent_model_hash()  # deterministic


def test_any_change_to_the_model_changes_the_lock() -> None:
    tampered = {**scent_model_record(), "decay_per_step": 0.20}
    assert canonical_sha256(tampered) != scent_model_hash()


def test_matching_scent_locks_agree() -> None:
    """`M6-005b`: two peers running the same model agree, lock and all."""
    my_terms = with_scent_lock(TERMS)
    offer = Handshake(dict(my_terms), identity={"group_id": "opp"}).signed()
    assert accept_offer(offer, my_terms)[SCENT_MODEL_TERM] == scent_model_hash()


def test_a_different_scent_model_is_refused_by_name() -> None:
    """A peer whose emission profile differs carries a different lock and is refused."""
    their_terms = {**TERMS, SCENT_MODEL_TERM: "deadbeef" * 8}
    offer = Handshake(their_terms).signed()
    with pytest.raises(AgreementError, match=SCENT_MODEL_TERM):
        accept_offer(offer, with_scent_lock(TERMS))


def test_the_negotiation_refuses_a_scent_mismatch_before_play() -> None:
    """`M5-015`: end to end — a scent-model deviation cancels the match at negotiation."""
    their_offer = Handshake({**TERMS, SCENT_MODEL_TERM: "0" * 64}).signed()
    with pytest.raises(NegotiationError, match=SCENT_MODEL_TERM):
        negotiate_match(
            handshake=Handshake(with_scent_lock(TERMS)),
            my_terms=with_scent_lock(TERMS),
            send_offer=lambda _o: None,
            take_offer=iter([their_offer]).__next__,
            clock=lambda: 0.0, sleep=lambda _s: None, timeout=5.0,
        )
