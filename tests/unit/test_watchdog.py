"""`M5-004c`/`M5-004d`: the system-wide freeze detector, proven without sleeping.

Book section 8.4.2: the Watchdog monitors the whole game loop, and when no heartbeat
has arrived for longer than the threshold it performs a **controlled shutdown** —
`persist_state()` to save the game for recovery, then `controlled_shutdown()` to
release MCP connections and close logs. Time is injected, so a freeze is exercised by
passing a number rather than by waiting minutes.
"""

import pytest

from p2p_thief_agent.services.watchdog import (
    Watchdog,
    WatchdogError,
    WatchdogState,
)

MATCH = {"network_and_league": {"watchdog_timeout_sec": 60}}


def make(persist=None, shutdown=None, *, timeout=60, started=0.0):
    """Build a watchdog with recording callbacks and a shared event log."""
    events: list[str] = []
    wd = Watchdog(
        timeout_sec=timeout,
        persist_state=persist or (lambda: events.append("persist")),
        controlled_shutdown=shutdown or (lambda: events.append("shutdown")),
        started=started,
    )
    return wd, events


def test_the_timeout_is_read_from_the_signed_match_object() -> None:
    """Both peers wait the same threshold because it is in the shared JSON `[AF-t19]`."""
    watchdog = Watchdog.from_match(
        MATCH, persist_state=lambda: None, controlled_shutdown=lambda: None, started=0.0
    )
    assert watchdog.timeout_sec == 60


def test_the_default_watchdog_timeout_is_appendix_f_sixty_seconds() -> None:
    """The book's 180s code sample is illustrative; Appendix F table 19 fixes 60."""
    watchdog = Watchdog.from_match(
        {}, persist_state=lambda: None, controlled_shutdown=lambda: None, started=0.0
    )
    assert watchdog.timeout_sec == 60


@pytest.mark.parametrize("bad", [0, -1])
def test_a_non_positive_timeout_is_refused(bad: int) -> None:
    with pytest.raises(WatchdogError, match="timeout must be positive"):
        Watchdog(
            timeout_sec=bad, persist_state=lambda: None,
            controlled_shutdown=lambda: None, started=0.0,
        )


def test_a_recent_heartbeat_keeps_the_system_alive() -> None:
    wd, events = make()
    assert wd.check(30.0) is WatchdogState.ALIVE
    assert wd.tripped is False and events == []


def test_the_boundary_itself_does_not_trip() -> None:
    """Book code trips on ``elapsed > timeout``: exactly at the threshold is still alive."""
    wd, events = make()
    assert wd.check(60.0) is WatchdogState.ALIVE
    assert wd.check(60.001) is WatchdogState.SHUTDOWN
    assert events == ["persist", "shutdown"]


def test_a_freeze_persists_then_shuts_down_in_that_order() -> None:
    """`persist_state()` saves the game for recovery *before* connections are released."""
    wd, events = make()
    assert wd.check(120.0) is WatchdogState.SHUTDOWN
    assert events == ["persist", "shutdown"], "state is saved before teardown"
    assert wd.tripped is True


def test_a_heartbeat_resets_the_window() -> None:
    """A live loop that keeps signalling is never torn down."""
    wd, events = make()
    wd.beat(55.0)
    assert wd.check(110.0) is WatchdogState.ALIVE, "measured from the last beat, not the start"
    assert events == []


def test_the_trip_fires_exactly_once() -> None:
    """A controlled shutdown is not a loop: later checks stay down without re-tearing."""
    wd, events = make()
    assert wd.check(120.0) is WatchdogState.SHUTDOWN
    assert wd.check(600.0) is WatchdogState.SHUTDOWN
    assert events == ["persist", "shutdown"], "persist and shutdown ran once, not twice"


def test_a_heartbeat_after_shutdown_is_refused() -> None:
    """A beat arriving after teardown means the loop is confused; fail closed."""
    wd, _ = make()
    wd.check(120.0)
    with pytest.raises(WatchdogError, match="after controlled shutdown"):
        wd.beat(130.0)


def test_a_failed_persist_still_releases_resources_and_surfaces() -> None:
    """If saving state fails, connections are still released and the error is not hidden."""
    events: list[str] = []

    def persist() -> None:
        events.append("persist")
        raise RuntimeError("disk full")

    wd, _ = make(persist=persist, shutdown=lambda: events.append("shutdown"))
    with pytest.raises(RuntimeError, match="disk full"):
        wd.check(120.0)
    assert events == ["persist", "shutdown"], "teardown runs even when persistence fails"
    assert wd.tripped is True
    assert wd.check(200.0) is WatchdogState.SHUTDOWN, "the trip is not re-run after it failed"
