"""M5-004f: rate limiting, and overflow that is queued rather than rejected.

The guidelines settle the design in one line — *"Overflow is queued, not rejected"* —
so the tests that matter are the ones proving work is **kept**, not dropped. Time is
injected, so a per-minute limit is exercised by moving a number instead of waiting.
"""

import pytest

from p2p_thief_agent.services.gatekeeper import (
    Gatekeeper,
    GatekeeperError,
    limits_from_match,
)

# The agreed gatekeeper block as it appears in the shared, signed match object.
MATCH = {"rate_limiter_gatekeeper": {
    "requests_per_minute": 30, "concurrent_requests": 2, "queue_depth": 100,
}}


def game() -> dict:
    return MATCH


def test_the_limits_come_from_the_signed_match_object() -> None:
    """Appendix F table 19 `Minimum` values, agreed by both peers."""
    assert limits_from_match(game()) == {
        "requests_per_minute": 30, "concurrent_requests": 2, "queue_depth": 100,
    }
    gate = Gatekeeper.from_match(game())
    assert (gate.requests_per_minute, gate.concurrent_requests, gate.queue_depth) == (30, 2, 100)


def test_calls_within_the_rate_and_concurrency_go_straight_out() -> None:
    gate = Gatekeeper(requests_per_minute=30, concurrent_requests=2, queue_depth=100)
    assert gate.submit("a", now=0.0) is True
    assert gate.submit("b", now=0.0) is True
    assert gate.queue_status().in_flight == 2
    assert gate.queue_status().depth == 0


def test_exceeding_concurrency_queues_rather_than_rejects() -> None:
    """The guidelines' rule: overflow is **kept**, and the caller is told to wait."""
    gate = Gatekeeper(concurrent_requests=2, queue_depth=10)
    gate.submit("a", now=0.0)
    gate.submit("b", now=0.0)

    assert gate.submit("c", now=0.0) is False, "queued, not rejected"
    assert gate.queue_status().depth == 1
    assert gate.queue_status().queued == 1


def test_finishing_a_call_frees_a_slot_and_drains_the_queue() -> None:
    gate = Gatekeeper(concurrent_requests=1, queue_depth=10)
    gate.submit("a", now=0.0)
    gate.submit("b", now=0.0)
    assert gate.queue_status().depth == 1

    gate.complete()
    assert gate.drain(now=0.0) == ["b"], "the queued work is released, never lost"
    assert gate.queue_status().depth == 0


def test_the_per_minute_rate_is_enforced_and_recovers_after_the_window() -> None:
    gate = Gatekeeper(requests_per_minute=3, concurrent_requests=99, queue_depth=10)
    for _ in range(3):
        assert gate.submit("x", now=10.0) is True

    assert gate.submit("y", now=10.0) is False, "the fourth in the same minute waits"

    # 60 s after the first three, the window has rolled and the queue drains.
    assert gate.drain(now=71.0) == ["y"]


def test_a_full_queue_refuses_loudly_rather_than_discarding() -> None:
    """The only case that fails — and it must never fail by silently dropping."""
    gate = Gatekeeper(concurrent_requests=1, queue_depth=2)
    gate.submit("in-flight", now=0.0)
    gate.submit("q1", now=0.0)
    gate.submit("q2", now=0.0)

    with pytest.raises(GatekeeperError, match="queue is full"):
        gate.submit("q3", now=0.0)
    assert gate.queue_status().depth == 2, "nothing already queued was thrown away"


def test_queue_status_reports_depth_capacity_and_totals() -> None:
    """Guidelines `get_queue_status`: a caller must be able to see the pressure."""
    gate = Gatekeeper(concurrent_requests=1, queue_depth=2)
    gate.submit("a", now=0.0)
    gate.submit("b", now=0.0)

    status = gate.queue_status()
    assert (status.depth, status.capacity, status.in_flight) == (1, 2, 1)
    assert (status.admitted, status.queued) == (1, 1)
    assert status.full is False

    gate.submit("c", now=0.0)
    assert gate.queue_status().full is True


def test_draining_an_empty_gate_is_harmless() -> None:
    assert Gatekeeper().drain(now=0.0) == []


def test_completing_more_than_was_started_cannot_go_negative() -> None:
    gate = Gatekeeper()
    gate.complete()
    assert gate.queue_status().in_flight == 0
