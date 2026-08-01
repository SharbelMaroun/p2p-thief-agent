"""`M5-004a`/`M5-004b`: bounded waiting, proven without sleeping.

The book's boxed note is the spec: *"Missing a Deadline is a Failure, Not Patience."*
So the tests that matter show the peer **stops** — a retry loop that quietly keeps
trying is the freeze the rule exists to prevent. Time is injected, so a timeout is
exercised by passing a number rather than by waiting.
"""

import pytest

from p2p_thief_agent.services.deadlines import (
    Deadline,
    DeadlineError,
    RetryPolicy,
    attempt,
    limits_from_match,
    read_limit,
)

MATCH = {
    "network_and_league": {"response_timeout_sec": 30, "watchdog_timeout_sec": 60},
    "rate_limiter_gatekeeper": {"retry_backoff_sec": 5, "max_retries": 3},
}


class Clock:
    """A hand-wound clock; `sleep` advances it exactly as the real one would."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start
        self.slept: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


def test_the_agreed_limits_are_read_from_the_signed_match_object() -> None:
    """Both peers are bound to the same numbers because they are in the signed JSON."""
    assert limits_from_match(MATCH) == {
        "response_timeout_sec": 30, "watchdog_timeout_sec": 60,
        "retry_backoff_sec": 5, "max_retries": 3,
    }


def test_the_defaults_match_appendix_f_table_19() -> None:
    """Verified against the book PDF 2026-08-01: 30 / 60 / 5 s / 3."""
    policy = RetryPolicy.from_match({})
    assert (policy.response_timeout_sec, policy.backoff_sec, policy.max_retries) == (30, 5, 3)
    assert policy.attempts == 4


@pytest.mark.parametrize("bad", [-1, True, "30", 1.5])
def test_a_nonsensical_limit_is_refused_rather_than_coerced(bad: object) -> None:
    with pytest.raises(DeadlineError, match="non-negative integer"):
        read_limit({"network_and_league": {"response_timeout_sec": bad}},
                   "network_and_league", "response_timeout_sec", 30)


def test_a_deadline_expires_at_its_boundary_not_after() -> None:
    """The instant the expiry is reached the request has failed, not a tick later."""
    deadline = Deadline.starting_at(100.0, 30)
    assert deadline.expired(129.9) is False
    assert deadline.expired(130.0) is True
    assert deadline.remaining(129.0) == pytest.approx(1.0)
    assert deadline.remaining(200.0) == 0.0


@pytest.mark.parametrize("bad", [0, -5])
def test_a_non_positive_timeout_is_refused(bad: int) -> None:
    with pytest.raises(DeadlineError, match="timeout must be positive"):
        Deadline.starting_at(0.0, bad)


def test_a_successful_call_is_not_retried() -> None:
    clock, calls = Clock(), []
    result = attempt(lambda: calls.append(1) or "ok", RetryPolicy(3, 5, 30),
                     clock=clock, sleep=clock.sleep)
    assert result == "ok"
    assert len(calls) == 1 and clock.slept == []


def test_a_flaky_call_succeeds_within_its_allowance() -> None:
    clock, calls = Clock(), []

    def flaky() -> str:
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("peer busy")
        return "ok"

    assert attempt(flaky, RetryPolicy(3, 5, 30), clock=clock, sleep=clock.sleep) == "ok"
    assert len(calls) == 3
    assert clock.slept == [5, 5], "each retry waits the agreed backoff"


def test_retries_are_bounded_and_the_peer_stops() -> None:
    """`AE-006`: running out of attempts is a decision, never a silent give-up."""
    clock, calls = Clock(), []

    def always_fails() -> None:
        calls.append(1)
        raise ConnectionError("unreachable")

    with pytest.raises(DeadlineError, match="exhausted 4 attempts"):
        attempt(always_fails, RetryPolicy(3, 5, 30), clock=clock, sleep=clock.sleep)
    assert len(calls) == 4, "the first try plus exactly three retries"


def test_an_attempt_that_overruns_its_expiry_is_not_retried() -> None:
    """A slow call is a failure, not patience — the retry budget does not rescue it."""
    clock = Clock()

    def slow() -> None:
        clock.now += 31
        raise TimeoutError("no answer")

    with pytest.raises(DeadlineError, match="exceeded its 30s expiry"):
        attempt(slow, RetryPolicy(3, 5, 30), clock=clock, sleep=clock.sleep)


def test_an_unexpected_error_kind_is_not_swallowed_by_the_retry_loop() -> None:
    """Retrying a programming error would hide it behind four identical failures."""
    with pytest.raises(ValueError, match="bad payload"):
        attempt(lambda: (_ for _ in ()).throw(ValueError("bad payload")),
                RetryPolicy(3, 5, 30), clock=Clock(), retry_on=(ConnectionError,))


def test_the_policy_reads_the_real_match_object() -> None:
    policy = RetryPolicy.from_match(MATCH)
    assert (policy.max_retries, policy.backoff_sec, policy.response_timeout_sec) == (3, 5, 30)
    assert policy.deadline(1000.0).expires == 1030.0
