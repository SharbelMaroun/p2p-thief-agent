"""Retry-aware delivery: transport faults retry, rejections don't (`M5-010`).

A sealed turn's bytes are idempotent — the receiver keys on ``(step, sender)`` — so
re-sending the same message after a transport fault is safe, and Appendix E rules 6/7
want a bounded retry rather than an instant surrender to a network blip. A content
rejection is the opposite: the opponent was reached and declined, so retrying it is
wrong and it must terminate the exchange (`M5-010b`).

This helper encodes exactly that asymmetry. It lives in the orchestration layer, which
coordinates the MCP Connector and the Deadline Tracker, so importing both the transport
error kinds and the retry primitive here is not a subsystem-to-subsystem link (`M5-001b`).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from p2p_thief_agent.adapters.fastmcp_client import TransportError
from p2p_thief_agent.services.deadlines import RetryPolicy, attempt

JsonObject = dict[str, object]
Send = Callable[[Mapping[str, object]], JsonObject]


def deliver(
    send: Send,
    message: Mapping[str, object],
    *,
    policy: RetryPolicy,
    clock: Callable[[], float],
    sleep: Callable[[float], None] = lambda _seconds: None,
) -> JsonObject:
    """Deliver ``message`` through ``send``, retrying only transport faults.

    Returns the opponent's acknowledgement. A ``PeerRejectionError`` is **not** in the
    retry set, so it propagates on the first occurrence (a decided game outcome, never a
    retry); a persistent ``TransportError`` raises ``DeadlineError`` once the budget is
    spent, so the caller can declare a technical loss and clear its queue.
    """
    return attempt(
        lambda: send(message),
        policy,
        clock=clock,
        sleep=sleep,
        retry_on=(TransportError,),
    )
