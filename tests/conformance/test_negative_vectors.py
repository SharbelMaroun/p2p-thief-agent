"""`M1-017`: the seven fail-closed categories, each tied to a numbered rule.

Every category maps to an Appendix E rule with a real sanction, verified in
`inst/police_thief_p2p_Summary.md` rather than taken from a notebook summary:

| category | rule | status | sanction |
| --- | --- | --- | --- |
| participant / config mismatch | 11 | Mandatory | "Disqualification of the game due to lack of symmetry" |
| hash mismatch at audit | 19 | Mandatory | "Iron rule; score of 0 for the falsifying group" |
| private leakage | 2 | Prohibited | "Immediate disqualification due to data leakage" |
| replay / flooding | 29 | Mandatory | "Locking of the interface" |

Two categories have no rule of their own, and saying so matters more than inventing one.
A **version** is one of the signed terms, so it refuses through rule 11's bit-for-bit
requirement rather than a rule about versions. **Ordering** has no rule at all, and the
reference does not gate ingestion on it either — it queues a duplicate for the peer loop.
So the stub accepts one by default and refuses only under `strict_ordering`, which is
ours, not the book's.
"""

from __future__ import annotations

import pytest

from tests.conformance.neutral_peer import ConformanceError
from tests.conformance.test_conformance import TERMS, _offer, _peer, _turn


def test_participant_mismatch_refuses(  ) -> None:
    """Rule 11, Mandatory: the configuration must be identical bit-for-bit."""
    with pytest.raises(ConformanceError, match="refusing to play"):
        _peer().negotiate(_offer({**TERMS, "board_size": 9}))


def test_a_version_or_any_signed_term_that_differs_refuses() -> None:
    """A version lives in the signed terms, so it refuses through the same rule 11 path."""
    with pytest.raises(ConformanceError, match="refusing to play"):
        _peer().negotiate(_offer({**TERMS, "schema_version": "9.9"}))


def test_a_wrong_value_type_refuses() -> None:
    with pytest.raises(ConformanceError, match="step must be an integer"):
        _peer().receive_turn(_turn(step="1"))  # type: ignore[arg-type]


def test_a_missing_required_field_refuses_and_names_it() -> None:
    """A bare refusal teaches the opponent nothing; rule 11's spirit is to name the term."""
    broken = _turn()
    del broken["smell_grid"]
    with pytest.raises(ConformanceError, match="smell_grid"):
        _peer().receive_turn(broken)


def test_a_hash_that_does_not_reproduce_refuses() -> None:
    """Rule 19, Mandatory, iron rule: score 0 for the falsifying group."""
    audit = {
        "sender": "x", "result_claim": "survival",
        "records": [{"payload": {"step": 1}, "nonce": "b" * 32, "commit": "0" * 64}],
    }
    with pytest.raises(ConformanceError, match="does not reproduce"):
        _peer().submit_audit(audit)


def test_private_state_on_the_wire_refuses() -> None:
    """Rule 2, Prohibited: immediate disqualification due to data leakage."""
    for leak in ("belief", "trust", "nonce"):
        with pytest.raises(ConformanceError, match="private state"):
            _peer().receive_turn(_turn(**{leak: 0.5}))


def test_a_replayed_step_is_refused_only_under_our_own_strictness() -> None:
    """**Ordering has no rule and the reference does not gate ingestion on it** — it
    queues a duplicate for the peer loop. So the stub accepts one by default, matching a
    real opponent, and refuses only with `strict_ordering` explicitly on. Marking that
    boundary matters: a stub stricter than every real peer would have us "fix" behaviour
    that was never wrong."""
    lenient = _peer()
    lenient.receive_turn(_turn(1))
    assert lenient.receive_turn(_turn(1)) == {"status": "received"}

    strict = _peer(strict_ordering=True)
    strict.receive_turn(_turn(1))
    with pytest.raises(ConformanceError, match="does not advance"):
        strict.receive_turn(_turn(1))


def test_unknown_fields_are_ignored_not_refused() -> None:
    """The `X-02` fix, from the receiving side: the reference ignores extras, and a peer
    that refused them would starve a classmate whose message was otherwise legal."""
    assert _peer().receive_turn(_turn(1, some_future_field=1)) == {"status": "received"}
