"""The Watchdog: a system-wide freeze detector (`M5-004c`, `M5-004d`).

Book section 8.4.2. While the Deadline Tracker (``services/deadlines.py``) bounds a
*single* request, the Watchdog watches the *whole* game loop. If no heartbeat has
arrived for longer than the threshold — a module crashed, or the network froze — it
performs a **controlled shutdown**: save the game so it can be recovered, then release
the MCP connections and close the logs. The book's page-83 sketch is::

    def watchdog_check(last_heartbeat, timeout_sec=180):
        elapsed = time.time() - last_heartbeat
        if elapsed > timeout_sec:
            persist_state()          # save game state for later recovery
            controlled_shutdown()    # release MCP connections, close logs
            return "SHUTDOWN"
        return "ALIVE"

Every difference from that sketch is deliberate and in this repository's grain:

- **Time is injected.** ``now`` is always a parameter, never a hidden ``time.time()``
  call, so a freeze is proven by passing a number rather than sleeping through it —
  the same discipline ``deadlines.py`` follows.
- **The threshold is negotiated, not hard-coded.** It comes from the shared, signed
  match object (``network_and_league.watchdog_timeout_sec``, default 60 `[AF-t19]`);
  the sample's 180 is illustrative, and Appendix F table 19 marks this value
  *Negotiation*. ``limits.WATCHDOG_TIMEOUT`` is the single place the key is written,
  shared with the Deadline Tracker without either subsystem importing the other.
- **`persist_state` and `controlled_shutdown` are injected callbacks.** This module
  owns *when* to persist and tear down and in *what order*; it never owns *how*.
- **The trip fires exactly once.** A controlled shutdown is not a loop: once it has
  run, later checks stay ``SHUTDOWN`` without persisting or tearing down again, and a
  heartbeat arriving after teardown is refused rather than reviving a dead loop.

The boundary follows the book code exactly — ``elapsed > timeout`` — so the instant
the threshold is *reached* is still alive and a tick past it trips. That differs from
``Deadline``, which treats its boundary as already expired; the two mechanisms use the
comparison the book gives each.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import StrEnum

from p2p_thief_agent.services.limits import WATCHDOG_TIMEOUT, read_limit


class WatchdogError(RuntimeError):
    """Raised on misconfiguration or a heartbeat after a controlled shutdown."""


class WatchdogState(StrEnum):
    """The two outcomes of a check, matching the book's return values."""

    ALIVE = "ALIVE"
    SHUTDOWN = "SHUTDOWN"


class Watchdog:
    """Monitor the game loop's heartbeat and shut down cleanly if it freezes."""

    __slots__ = ("_timeout", "_persist", "_shutdown", "_last_heartbeat", "_tripped")

    def __init__(
        self,
        *,
        timeout_sec: float,
        persist_state: Callable[[], None],
        controlled_shutdown: Callable[[], None],
        started: float,
    ) -> None:
        if timeout_sec <= 0:
            raise WatchdogError(f"timeout must be positive, got {timeout_sec!r}")
        self._timeout = timeout_sec
        self._persist = persist_state
        self._shutdown = controlled_shutdown
        self._last_heartbeat = started
        self._tripped = False

    @classmethod
    def from_match(
        cls,
        game: Mapping,
        *,
        persist_state: Callable[[], None],
        controlled_shutdown: Callable[[], None],
        started: float,
    ) -> Watchdog:
        """Build a watchdog whose threshold is the agreed ``watchdog_timeout_sec``."""
        return cls(
            timeout_sec=read_limit(game, *WATCHDOG_TIMEOUT),
            persist_state=persist_state,
            controlled_shutdown=controlled_shutdown,
            started=started,
        )

    @property
    def timeout_sec(self) -> float:
        """Return the freeze threshold in seconds."""
        return self._timeout

    @property
    def tripped(self) -> bool:
        """Return whether the controlled shutdown has already run."""
        return self._tripped

    def beat(self, now: float) -> None:
        """Record a heartbeat from the live loop, refusing one after shutdown."""
        if self._tripped:
            raise WatchdogError("heartbeat arrived after controlled shutdown")
        self._last_heartbeat = now

    def check(self, now: float) -> WatchdogState:
        """Return ``ALIVE``, or trip the controlled shutdown once and return ``SHUTDOWN``.

        The trip is idempotent: after it has run, this returns ``SHUTDOWN`` without
        persisting or tearing down a second time. Teardown runs even if persistence
        raises — a controlled shutdown must release its connections regardless — and
        the persistence error is then surfaced rather than swallowed.
        """
        if self._tripped:
            return WatchdogState.SHUTDOWN
        if now - self._last_heartbeat > self._timeout:
            self._tripped = True
            try:
                self._persist()
            finally:
                self._shutdown()
            return WatchdogState.SHUTDOWN
        return WatchdogState.ALIVE
