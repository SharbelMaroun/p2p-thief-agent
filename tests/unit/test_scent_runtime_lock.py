"""`M6-022`: a runtime assertion keeps the scent physics identical to the locked model.

The negotiation lock (`M6-005`) proves the two peers *agreed* on a model; this proves the
code that actually runs still *is* that model, so a later drift fails loudly rather than
emitting fields the opponent's audit would reject (`AE-23`).
"""

import pytest

from p2p_thief_agent.perception.scent_lock import (
    ScentLockError,
    assert_scent_locked,
    scent_model_hash,
)


def test_the_runtime_assertion_passes_when_the_model_matches() -> None:
    assert assert_scent_locked(scent_model_hash()) is None


def test_the_runtime_assertion_fails_on_a_drifted_or_foreign_model() -> None:
    with pytest.raises(ScentLockError, match="does not match the locked model"):
        assert_scent_locked("0" * 64)
