"""Wait for the opponent to come up, because start order must not matter (M5-019e).

Two peers launched by two people on two machines cannot start simultaneously. The
reference is explicit that **"start order doesn't matter"** and retries until the
opponent's server answers, governed by two private keys (confirmed 2026-08-02):
``connect_timeout_seconds`` (60) bounds the whole wait, ``retry_interval_seconds``
(1.0) is the gap between attempts.

**Why this is not `services/deadlines.py` or `services/watchdog.py`.** Those two
exist to make waiting a *failure*: rule 6 requires a deadline "to prevent deadlocks
while waiting for the opponent", and past expiry is a technical loss. Startup is the
one phase where an unreachable peer is **expected and harmless** — before the game
exists there is nothing to forfeit, so patience is correct here and wrong everywhere
else. Keeping it a separate module is what stops that leniency leaking into the match.

It is still bounded. A peer that waits forever for an opponent who never starts is a
hang with no signal to its operator, which is the same defect in a friendlier costume.

Time and the probe are injected, so start-order tolerance is proven by advancing a
number rather than by sleeping on a socket `[ADR-0009]`.
"""

from __future__ import annotations

from collections.abc import Callable

# Return True when the opponent answers. Must not raise: an unreachable peer during
# startup is the expected case, not an error, so a probe that throws is a bug in the
# probe rather than a verdict about the opponent.
Probe = Callable[[], bool]
Clock = Callable[[], float]
Sleep = Callable[[float], None]

DEFAULT_CONNECT_TIMEOUT = 60.0
DEFAULT_RETRY_INTERVAL = 1.0


class ReadinessError(ValueError):
    """Raised when a readiness bound is not usable."""


def wait_for_peer(
    probe: Probe,
    *,
    clock: Clock,
    sleep: Sleep,
    timeout: float = DEFAULT_CONNECT_TIMEOUT,
    interval: float = DEFAULT_RETRY_INTERVAL,
) -> bool:
    """Poll ``probe`` until the opponent answers; return whether it ever did.

    Returns ``True`` on the first successful probe and ``False`` once the budget is
    spent, so the caller decides what an absent opponent means. It deliberately does
    **not** raise: "nobody started the other peer yet" is an operator situation, not
    a protocol fault, and turning it into an exception would blur it with the
    in-match failures that really are.

    The probe runs **before** the clock is consulted, so an opponent already up is
    found immediately even with a zero budget.
    """
    if interval <= 0:
        raise ReadinessError(f"interval must be positive, got {interval!r}")
    if timeout < 0:
        raise ReadinessError(f"timeout must not be negative, got {timeout!r}")

    deadline = clock() + timeout
    while True:
        if probe():
            return True
        if clock() >= deadline:
            return False
        sleep(interval)


def timeouts_from_private_config(config: object) -> tuple[float, float]:
    """Read ``connect_timeout_seconds`` / ``retry_interval_seconds`` from private TOML.

    These are **private** values: they govern only how patiently this peer waits for
    its opponent to appear, so they never enter the signed match object and cannot
    affect a hash or the game's terms. Both fall back to the reference's shipped
    defaults when absent, which is safe precisely because neither can change the
    outcome of a match -- only how long a human waits before seeing a failure.
    """
    section = getattr(config, "get", lambda _k: None)("network")
    if not isinstance(section, dict):
        return DEFAULT_CONNECT_TIMEOUT, DEFAULT_RETRY_INTERVAL
    timeout = section.get("connect_timeout_seconds", DEFAULT_CONNECT_TIMEOUT)
    interval = section.get("retry_interval_seconds", DEFAULT_RETRY_INTERVAL)
    return float(timeout), float(interval)
