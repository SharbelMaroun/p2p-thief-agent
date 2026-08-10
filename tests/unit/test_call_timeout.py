"""Every outbound call is capped strictly below the deadline we signed.

Guards the 2026-08-10 addition, the same defect the companion Cop carried. `FastMCPClient`
has always accepted a `timeout`, but `serve` never passed one, so live calls were unbounded.
Nothing failed under test: the breach is arithmetic, and it surfaces only when a real peer
accepts a push and then goes quiet.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.services.deadlines import RetryPolicy
from p2p_thief_agent.services.limits import call_timeout_sec

APPENDIX_F = RetryPolicy(max_retries=3, backoff_sec=5.0, response_timeout_sec=30.0)


def test_cap_is_strictly_under_the_signed_deadline() -> None:
    """The whole purpose: a cap equal to the deadline leaves a retry no room."""
    assert APPENDIX_F.call_timeout_sec < APPENDIX_F.response_timeout_sec


def test_every_permitted_attempt_fits_inside_the_deadline() -> None:
    """`attempts` calls at the cap must not outlive the budget they are drawn from."""
    assert APPENDIX_F.call_timeout_sec * APPENDIX_F.attempts <= APPENDIX_F.response_timeout_sec


@pytest.mark.parametrize("retries", range(0, 6))
def test_cap_stays_legal_for_any_negotiated_retry_count(retries: int) -> None:
    """Opponents negotiate different retry counts; the invariant may not depend on ours."""
    policy = RetryPolicy(max_retries=retries, backoff_sec=5.0, response_timeout_sec=30.0)
    assert 0 < policy.call_timeout_sec < policy.response_timeout_sec
    assert policy.call_timeout_sec * policy.attempts <= policy.response_timeout_sec


def test_unnegotiated_path_is_bounded_too() -> None:
    """`serve` builds the transport before a config exists; that path must not be unlimited."""
    assert call_timeout_sec(None) == APPENDIX_F.call_timeout_sec


def test_a_signed_config_tightens_the_cap() -> None:
    """A peer signing a shorter deadline must shorten our calls, not just our bookkeeping.

    Note the two sections: the deadline is `network_and_league.response_timeout_sec` but the
    retry count is `rate_limiter_gatekeeper.max_retries`. Writing both under one section makes
    the cap silently fall back to Appendix F's default instead of failing -- which is how this
    test was wrong the first time it ran.
    """
    tight = {
        "network_and_league": {"response_timeout_sec": 6},
        "rate_limiter_gatekeeper": {"max_retries": 1, "retry_backoff_sec": 1},
    }
    assert call_timeout_sec(tight) == 3.0


@pytest.mark.parametrize("retries", range(0, 6))
def test_both_implementations_agree(retries: int) -> None:
    """`services.limits` and `RetryPolicy` express one rule twice; they must not drift.

    The duplication is deliberate — the MCP connector may not import the deadline-tracker
    subsystem, so the arithmetic lives in neutral infrastructure and the policy mirrors it.
    Deliberate duplication still needs a guard.
    """
    game = {
        "network_and_league": {"response_timeout_sec": 30},
        "rate_limiter_gatekeeper": {"max_retries": retries, "retry_backoff_sec": 5},
    }
    assert call_timeout_sec(game) == RetryPolicy.from_match(game).call_timeout_sec
