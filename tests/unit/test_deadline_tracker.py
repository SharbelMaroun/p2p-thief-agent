"""`M5-009`: the Deadline Tracker subsystem — reap expired requests, clear on a loss.

Book §8.4.1: a request past its expiry is a failure, reaped, never awaited. This
subsystem registers each outbound request with a deadline from the agreed limits, reaps
the ones past expiry, and — when a technical loss is declared — clears the queue cleanly
so no orphaned pending request survives (`M5-009b`). Time is injected.
"""

import pytest

from p2p_thief_agent.services.deadline_tracker import DeadlineTrackerError, RequestTracker

MATCH = {"network_and_league": {"response_timeout_sec": 30}}


def tracker() -> RequestTracker:
    return RequestTracker.from_match(MATCH)


def test_a_request_gets_an_expiry_from_the_agreed_limits() -> None:
    t = tracker()
    assert t.track("turn-1", now=100.0).expires == 130.0
    assert t.pending == ("turn-1",)


def test_a_completed_request_is_no_longer_tracked() -> None:
    t = tracker()
    t.track("turn-1", now=100.0)
    t.complete("turn-1")
    assert t.pending == ()


def test_completing_an_unknown_request_is_a_no_op() -> None:
    tracker().complete("never-tracked")  # must not raise


def test_a_duplicate_in_flight_request_is_refused() -> None:
    t = tracker()
    t.track("turn-1", now=100.0)
    with pytest.raises(DeadlineTrackerError, match="already in flight"):
        t.track("turn-1", now=101.0)


def test_expired_requests_are_reaped_and_live_ones_kept() -> None:
    t = tracker()
    t.track("slow", now=0.0)  # expires at 30
    t.track("fresh", now=100.0)  # expires at 130
    assert t.reap(now=50.0) == ("slow",)
    assert t.pending == ("fresh",)


def test_reap_returns_nothing_when_all_requests_are_live() -> None:
    t = tracker()
    t.track("a", now=100.0)
    assert t.reap(now=120.0) == ()
    assert t.pending == ("a",)


def test_clear_drops_every_pending_request_on_a_technical_loss() -> None:
    t = tracker()
    t.track("a", now=100.0)
    t.track("b", now=100.0)
    assert set(t.clear()) == {"a", "b"}
    assert t.pending == ()


def test_deadline_satisfies_the_gateway_port() -> None:
    assert tracker().deadline(1000.0).expires == 1030.0
