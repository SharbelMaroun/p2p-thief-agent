"""`M6-005`/`M5-015`: lock, publish, and verify the scent model at negotiation (`AE-23`).

The lock rides **beside** the signed terms, not inside them, and is checked leniently:
an opponent that publishes none is still played, one whose model differs is refused
before the first move. That asymmetry is the whole design — rule 23 sanctions a
*deviation*, and the pinned simulator publishes no standalone scent hash at all, so
requiring one would refuse every simulator-built classmate over a message it never
sends.

The digest pinned here is a **cross-implementation** constant: the companion Cop peer,
written independently against the same book sections, produces the same value from its
own record. Pinning it means a change to the record shape fails here rather than in a
match, where both peers would refuse each other with no idea why.
"""

import pytest

from p2p_thief_agent.orchestration.negotiation import NegotiationError, negotiate_match
from p2p_thief_agent.perception.scent import DEFAULT_OUTER_RING_DELTA, ScentModelError
from p2p_thief_agent.perception.scent_lock import (
    SCENT_LOCK_FIELD,
    SCENT_OUTER_RING_FIELD,
    ScentLockError,
    assert_scent_locked,
    scent_lock_fields,
    scent_model_hash,
    scent_model_record,
    verify_peer_scent_lock,
)
from p2p_thief_agent.protocol.agreement import AgreementError, accept_offer
from p2p_thief_agent.protocol.crypto import canonical_sha256
from p2p_thief_agent.protocol.handshake import Handshake

TERMS = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.10, "emit_intensity": 0.9,
    "max_steps": 35, "barriers_max": 14, "thief_start": [0, 0], "cop_start": [6, 6],
    "num_games": 6,
}

# The lock over the default model, reproduced independently by the Cop peer.
#
# Moved 2026-08-16 from `e6aef097...` when the upper clamp entered the declared `update`
# string (`U-031`). The old value is worth remembering rather than deleting: the clamp
# reached this repository's *physics* days earlier, and only the declaration lagged, so
# between those dates this constant asserted agreement with the Cop that no longer held --
# the Cop answered `c77a1260...` while this peer answered `e6aef097...`, and the test that
# exists precisely to catch a cross-peer split went on passing.
#
# It could not catch it: the digest is recomputed from THIS repository alone, so a literal
# updated on one side only records agreement instead of checking it. The real cross-peer
# check is `export_scent_parity.py`/`test_scent_parity`, which compares emitted fields.
AGREED_DEFAULT_LOCK = "c77a12609b9f1c3df90067ce166b6b0455c8343dba9d463b0e8e402f8469b34f"


def test_the_record_carries_the_formula_constants_field_and_profile() -> None:
    """`M6-005a`: one canonical record, hashable to a stable lock."""
    record = scent_model_record()
    assert record["decay_per_step"] == 0.10
    assert record["center_intensity"] == 0.9
    assert record["field_size"] == 5
    assert record["emission_profile_by_squared_distance"]["0"] == 0.90
    assert "max(0" in record["update"]  # the formula itself is inside the lock
    assert scent_model_hash() == scent_model_hash()  # deterministic


def test_the_lock_matches_the_independently_written_peer() -> None:
    """Two implementations, one digest — the point of locking a model at all."""
    assert scent_model_hash() == AGREED_DEFAULT_LOCK


def test_any_change_to_the_model_changes_the_lock() -> None:
    tampered = {**scent_model_record(), "decay_per_step": 0.20}
    assert canonical_sha256(tampered) != scent_model_hash()


def test_the_negotiated_ring_is_inside_the_lock() -> None:
    """`U-025`: disagreeing on the eight unnamed cells is a visible disagreement."""
    assert scent_model_hash(0.07) != scent_model_hash(DEFAULT_OUTER_RING_DELTA)


def test_the_published_fields_carry_both_the_lock_and_the_value_it_covers() -> None:
    fields = scent_lock_fields()
    assert fields[SCENT_LOCK_FIELD] == AGREED_DEFAULT_LOCK
    assert fields[SCENT_OUTER_RING_FIELD] == DEFAULT_OUTER_RING_DELTA


def test_a_peer_publishing_no_lock_is_still_playable() -> None:
    """The reference publishes none; requiring one would refuse every such classmate."""
    verify_peer_scent_lock(None)
    offer = Handshake(dict(TERMS)).signed()
    assert accept_offer(offer, TERMS, expected_scent_lock=scent_model_hash())


def test_a_peer_running_our_model_is_accepted() -> None:
    verify_peer_scent_lock(AGREED_DEFAULT_LOCK)
    offer = {**Handshake(dict(TERMS)).signed(), **scent_lock_fields()}
    assert accept_offer(offer, TERMS, expected_scent_lock=scent_model_hash())


def test_a_peer_whose_model_differs_is_refused_by_name() -> None:
    with pytest.raises(ScentLockError, match="rule 23"):
        verify_peer_scent_lock("f" * 64)
    offer = {**Handshake(dict(TERMS)).signed(), SCENT_LOCK_FIELD: "deadbeef" * 8}
    with pytest.raises(AgreementError, match=SCENT_LOCK_FIELD):
        accept_offer(offer, TERMS, expected_scent_lock=scent_model_hash())


def test_the_negotiation_refuses_a_scent_deviation_before_play() -> None:
    """`M5-015`: end to end — a differing emission model cancels the match."""
    their_offer = {**Handshake(dict(TERMS)).signed(), SCENT_LOCK_FIELD: "0" * 64}
    with pytest.raises(NegotiationError, match=SCENT_LOCK_FIELD):
        negotiate_match(
            handshake=Handshake(dict(TERMS)),
            my_terms=TERMS,
            send_offer=lambda _o: None,
            take_offer=iter([their_offer]).__next__,
            clock=lambda: 0.0, sleep=lambda _s: None, timeout=5.0,
        )


def test_the_negotiation_publishes_our_lock_on_the_offer_we_send() -> None:
    """A lock nobody can see cannot be compared, so it must go out with the offer."""
    sent: list = []
    with pytest.raises(NegotiationError):  # no reply; we only care what was sent
        negotiate_match(
            handshake=Handshake(dict(TERMS)),
            my_terms=TERMS,
            send_offer=sent.append,
            take_offer=lambda: None,
            clock=iter([0.0, 99.0]).__next__, sleep=lambda _s: None, timeout=5.0,
        )
    assert sent[0][SCENT_LOCK_FIELD] == AGREED_DEFAULT_LOCK
    assert sent[0][SCENT_OUTER_RING_FIELD] == DEFAULT_OUTER_RING_DELTA


def test_the_running_model_is_checked_against_what_was_locked() -> None:
    assert_scent_locked(AGREED_DEFAULT_LOCK)
    with pytest.raises(ScentLockError, match="does not match"):
        assert_scent_locked(AGREED_DEFAULT_LOCK, outer_ring=0.07)


def test_an_out_of_range_ring_cannot_be_locked_at_all() -> None:
    with pytest.raises(ScentModelError):
        scent_model_hash(1.5)
