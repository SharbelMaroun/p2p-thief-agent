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

import time
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


def retrying_deliver(
    game_config: Mapping[str, object] | None,
    sleep: Callable[[float], None],
    clock: Callable[[], float] = time.monotonic,
) -> Callable[[Send, Mapping[str, object]], JsonObject]:
    """Bind the **agreed** retry budget onto a send, for the live match paths.

    Lives here rather than beside its callers because binding the budget needs both the
    MCP Connector's error kinds and the Deadline Tracker's policy, and only the
    orchestration layer may join two subsystems (`M5-001b`) — a helper in `adapters/`
    would be exactly the direct subsystem-to-subsystem link the gateway exists to prevent.

    `RetryPolicy.from_match` reads `max_retries` and `retry_backoff_sec` out of the
    **signed** match object, so neither peer can quietly give itself a longer rope; with
    no negotiated config (a bare `--peer` development run) the Appendix F defaults apply.

    A limit this cannot parse falls back to those defaults rather than raising. Reading a
    retry budget is a *reliability* concern, and refusing to play because the retry policy
    itself would not load turns a resilience feature into a new way to lose a match —
    strictly worse than the single-attempt behaviour it replaced. Appendix F conformance
    of the agreed values is `protocol/agreement.check_appendix_f`'s job, at negotiation,
    where a bad value is refused **by name** before either peer commits to anything.
    """
    try:
        policy = RetryPolicy.from_match(game_config or {})
    except Exception:  # noqa: BLE001 - see above: never fail a match over the retry policy
        policy = RetryPolicy.from_match({})

    def deliver_with_retry(send: Send, message: Mapping[str, object]) -> JsonObject:
        return deliver(send, message, policy=policy, clock=clock, sleep=sleep)

    return deliver_with_retry
