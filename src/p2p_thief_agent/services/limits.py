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
