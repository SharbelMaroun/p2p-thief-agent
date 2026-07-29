"""Unit tests for M3-003 accepted scoring and terminal-outcome calculation."""

import pytest

from p2p_thief_agent.domain import DomainError
from p2p_thief_agent.state.scoring import (
    CAPTURE_COP,
    CAPTURE_THIEF,
    DEFAULT_SURVIVAL_THRESHOLD,
    SURVIVAL_COP,
    SURVIVAL_THIEF,
    TECHNICAL_LOSS_SCORE,
    TIE_SCORE,
    Outcome,
    resolve_outcome,
    thief_score,
)


def test_fixed_table_17_constants():
    # Appendix F Table 17 FIXED points, verbatim.
    assert (CAPTURE_COP, CAPTURE_THIEF) == (20, 5)
    assert (SURVIVAL_COP, SURVIVAL_THIEF) == (5, 10)
    assert TIE_SCORE == 2
    assert TECHNICAL_LOSS_SCORE == 0
    assert DEFAULT_SURVIVAL_THRESHOLD == 35


def test_thief_score_for_every_outcome():
    assert thief_score(Outcome.CAPTURE) == 5
    assert thief_score(Outcome.SURVIVAL) == 10
    assert thief_score(Outcome.TIE) == 2
    assert thief_score(Outcome.TECHNICAL_LOSS) == 0


def test_thief_score_rejects_non_outcome():
    with pytest.raises(DomainError):
        thief_score("capture")


def test_capture_is_terminal():
    assert resolve_outcome(captured=True, steps=3) is Outcome.CAPTURE


def test_survival_at_threshold():
    assert resolve_outcome(captured=False, steps=35, survival_threshold=35) is Outcome.SURVIVAL
    assert resolve_outcome(captured=False, steps=36, survival_threshold=35) is Outcome.SURVIVAL


def test_in_progress_returns_none():
    assert resolve_outcome(captured=False, steps=34, survival_threshold=35) is None


def test_technical_loss_overrides_capture_and_survival():
    assert (
        resolve_outcome(captured=True, steps=99, survival_threshold=35, technical_loss=True)
        is Outcome.TECHNICAL_LOSS
    )


def test_capture_outranks_survival_when_both_hold():
    # A Thief caught exactly at the horizon is captured, not a survivor.
    assert resolve_outcome(captured=True, steps=35, survival_threshold=35) is Outcome.CAPTURE


@pytest.mark.parametrize("bad", [-1])
def test_negative_values_reject(bad):
    with pytest.raises(DomainError):
        resolve_outcome(captured=False, steps=bad)
    with pytest.raises(DomainError):
        resolve_outcome(captured=False, steps=1, survival_threshold=bad)


@pytest.mark.parametrize("bad", [True, 1.0, "x"])
def test_non_integer_steps_reject(bad):
    with pytest.raises(DomainError):
        resolve_outcome(captured=False, steps=bad)


def test_non_bool_flags_reject():
    with pytest.raises(DomainError):
        resolve_outcome(captured=1, steps=0)
    with pytest.raises(DomainError):
        resolve_outcome(captured=False, steps=0, technical_loss=1)
