"""Shared reading of the signed match object's reliability limits.

The Deadline Tracker and the Watchdog are separate orchestrator subsystems (`M5-001`)
that must not import each other (`M5-001b`), yet both read agreed limits out of the same
shared, signed match object. This module is the neutral helper they both depend on — it
is infrastructure, not one of the five subsystems, so importing it is not a
subsystem-to-subsystem link.

All four limits live in the shared, signed match object, so neither peer can quietly
give itself a longer rope. Appendix F table 19 marks the response timeout, retry backoff,
and max retries `Minimum`, and the watchdog timeout `Negotiation` `[AF-t19]`.
"""

from __future__ import annotations

from collections.abc import Mapping

RESPONSE_TIMEOUT = ("network_and_league", "response_timeout_sec", 30)
WATCHDOG_TIMEOUT = ("network_and_league", "watchdog_timeout_sec", 60)
RETRY_BACKOFF = ("rate_limiter_gatekeeper", "retry_backoff_sec", 5)
MAX_RETRIES = ("rate_limiter_gatekeeper", "max_retries", 3)


# Headroom kept back from the signed response deadline for transport: TLS, the tunnel hop, and
# the peer's own dispatch. Only binds when a peer negotiates zero retries, where dividing the
# budget by the attempt count would otherwise hand a single call the entire deadline.
MARGIN = 0.9


class LimitError(ValueError):
    """Raised when an agreed limit is present but not a non-negative integer."""


def read_limit(game: Mapping, section: str, key: str, default: int) -> int:
    """Return one agreed limit, falling back to the Appendix F default."""
    block = game.get(section)
    value = block.get(key) if isinstance(block, Mapping) else None
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LimitError(f"{section}.{key} must be a non-negative integer, got {value!r}")
    return value


def call_timeout_sec(game: Mapping | None = None) -> float:
    """Cap one outbound call so a *retry* still fits inside the signed deadline.

    Lives here rather than beside ``RetryPolicy`` for the reason this module exists at all: the
    MCP connector needs the cap when it builds the transport, and ``adapters`` importing
    ``services.deadlines`` is a subsystem-to-subsystem link the orchestrator boundary forbids
    (`M5-001b`) — ``test_orchestrator_boundary`` caught exactly that on the first attempt. This
    module is neutral infrastructure, so both may depend on it.

    ``attempts`` calls at the cap must fit the whole deadline, which makes the signed budget
    over the attempt count the largest legal cap: 7.5s of a 30s deadline at Appendix F's three
    retries. ``MARGIN`` binds only at **zero** negotiated retries, where ``attempts`` is 1 and
    the division alone would hand one call the entire deadline with nothing left for transport.

    ``game`` may be ``None``: ``serve`` reaches the transport before negotiation, and Appendix
    F's defaults keep that path bounded instead of leaving the gap this cap closes.
    """
    game = game if isinstance(game, Mapping) else {}
    deadline = float(read_limit(game, *RESPONSE_TIMEOUT))
    attempts = read_limit(game, *MAX_RETRIES) + 1
    return min(deadline / attempts, deadline * MARGIN)
