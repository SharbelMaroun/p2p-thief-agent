"""`M5-014`: whether this peer agrees to play, and what it says when it will not.

Rule 11 makes refusal mandatory on any mismatch, so most cases here are refusals --
each asserted to name the term at fault, since a refusal an opponent cannot act on
is worth little to either side.
"""

import pytest

from p2p_thief_agent.protocol.agreement import (
    AgreementError,
    accept_offer,
    differing_terms,
    signed_offer_is_valid,
    validate_participants,
)
from p2p_thief_agent.protocol.crypto import commit_of
from p2p_thief_agent.protocol.handshake import Handshake, config_sha256

NONCE = "0123456789abcdef0123456789abcdef"

# A complete, Appendix-F-legal agreement, matching the reference's key set exactly:
# `min_center_intensity` is present because `terms_from_config` always emits it.
TERMS = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.10, "emit_intensity": 0.9,
    "min_center_intensity": 0.05, "max_steps": 35, "barriers_max": 14,
    "setting": "New York", "hint_max_words": 15, "axis_origin_corner": "top-left",
    "axis_start_index": 0, "thief_start": [3, 3], "cop_start": [0, 0], "num_games": 6,
}


def offer(**changes: object) -> dict:
    terms = {**TERMS, **changes}
    return {"terms": terms, "nonce": NONCE, "signature": commit_of(terms, NONCE)}


def test_the_baseline_agreement_is_acceptable() -> None:
    assert accept_offer(offer(), TERMS) == TERMS



def test_a_mismatch_names_every_offending_term() -> None:
    mine = {**TERMS, "hint_max_words": 20, "setting": "Paris"}
    with pytest.raises(AgreementError, match="hint_max_words, setting"):
        accept_offer(offer(), mine)


def test_a_term_the_opponent_omits_counts_as_a_disagreement() -> None:
    """An absent term must not read as a silent default agreement."""
    assert differing_terms(TERMS, {k: v for k, v in TERMS.items() if k != "setting"}) == ["setting"]


def test_a_missing_required_term_is_refused_by_name() -> None:
    """The reference fails fast on exactly this, so a peer must expect it."""
    thin = {**TERMS, "min_center_intensity": None}
    with pytest.raises(AgreementError, match="missing required agreed term"):
        accept_offer({"terms": thin, "nonce": NONCE, "signature": commit_of(thin, NONCE)}, thin)


def test_terms_tampered_with_after_signing_are_refused() -> None:
    message = offer()
    message["terms"]["board_size"] = 9
    with pytest.raises(AgreementError, match="signature"):
        accept_offer(message, TERMS)


@pytest.mark.parametrize("field", ["terms", "nonce", "signature"])
def test_a_structurally_incomplete_offer_is_refused(field: str) -> None:
    message = offer()
    del message[field]
    with pytest.raises(AgreementError, match=field):
        accept_offer(message, TERMS)


def test_non_object_terms_are_refused() -> None:
    with pytest.raises(AgreementError, match="must be an object"):
        accept_offer({"terms": ["board_size"], "nonce": NONCE, "signature": "x"}, TERMS)


@pytest.mark.parametrize(
    "participants",
    [["only-one"], ["a", "a"], ["a", ""], "not-a-list", ["a", "b", "c"], [1, 2]],
)
def test_bad_participant_lists_are_refused(participants: object) -> None:
    with pytest.raises(AgreementError):
        validate_participants(participants)


def test_a_group_outside_the_agreement_is_refused() -> None:
    with pytest.raises(AgreementError, match="not one of the participants"):
        validate_participants(["thief-team", "cop-team"], "some-stranger")


def test_signed_offer_is_valid_reports_without_raising() -> None:
    assert signed_offer_is_valid(offer()) is True
    assert signed_offer_is_valid({"terms": TERMS, "nonce": NONCE, "signature": "0" * 64}) is False
    assert signed_offer_is_valid({"terms": TERMS}) is False


def test_agreement_implies_an_identical_config_hash() -> None:
    """`M5-014b`: accepting and hashing must not be able to disagree.

    Comparing terms is stronger than comparing `config_sha256` -- only it can say
    *what* differs -- but both must reach the same verdict, or one is wrong.
    """
    agreed = accept_offer(offer(), TERMS)
    assert config_sha256(agreed) == config_sha256(TERMS)

    divergent = {**TERMS, "hint_max_words": 20}
    assert config_sha256(divergent) != config_sha256(TERMS)
    with pytest.raises(AgreementError, match="hint_max_words"):
        accept_offer(offer(), divergent)


def test_both_directions_agree_on_the_same_terms() -> None:
    """`M5-014e`: proposing and accepting must both pass, unedited."""
    thief = Handshake(terms=dict(TERMS), identity={"group_id": "thief-team"})
    cop_side = Handshake(terms=dict(TERMS), identity={"group_id": "cop-team"})
    assert accept_offer(thief.signed(), cop_side.terms) == TERMS
    assert accept_offer(cop_side.signed(), thief.terms) == TERMS
