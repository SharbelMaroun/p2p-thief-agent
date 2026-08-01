"""`M5-019`: the polling turn source that lets a peer play a match unattended.

The mailbox (`adapters.build_server`) only enqueues; `run_turn` only consumes.
Nothing joined them, which is why a full game needed a harness feeding messages in
by hand. These tests pin the join.

Two properties matter more than the mechanics, both from the book: a wait must be
**bounded** (rule 6 -- a deadline "to prevent deadlocks while waiting for the
opponent"), and a waiting peer must still **pulse** (section 8.4.2 puts the
watchdog on the main game loop, and waiting is exactly when a frozen peer and a
patient one look alike). Time is injected, so every timeout below is proven by
advancing a number rather than by sleeping.
"""

import pytest

from p2p_thief_agent.orchestration.polling import PollingError, poll_for_turn


class FakeClock:
    """A clock that only moves when something sleeps, so waiting is observable."""

    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


def queued(*messages: dict) -> object:
    """A take-source that yields each message once, then nothing."""
    pending = list(messages)

    def take() -> dict | None:
        return pending.pop(0) if pending else None

    return take


def silence() -> object:
    return lambda: None


def test_a_turn_already_in_the_mailbox_is_returned_without_waiting() -> None:
    clock = FakeClock()
    got = poll_for_turn(
        queued({"step": 1}), clock=clock.time, sleep=clock.sleep, timeout=30.0
    )
    assert got == {"step": 1}
    assert clock.slept == []


def test_a_turn_already_queued_is_taken_even_with_no_time_budget() -> None:
    """The deadline bounds *waiting*; it must not refuse a message already here.

    Forfeiting a match because a turn arrived while the budget was spent would be
    losing on a technicality, and the opponent did nothing wrong.
    """
    clock = FakeClock()
    got = poll_for_turn(
        queued({"step": 4}), clock=clock.time, sleep=clock.sleep, timeout=0.0
    )
    assert got == {"step": 4}


def test_a_turn_that_arrives_after_several_polls_is_returned() -> None:
    clock = FakeClock()
    take = queued(None, None, {"step": 2})  # type: ignore[arg-type]
    got = poll_for_turn(
        take, clock=clock.time, sleep=clock.sleep, timeout=30.0, poll_interval=0.5
    )
    assert got == {"step": 2}
    assert clock.slept == [0.5, 0.5]


def test_sustained_silence_returns_none_at_the_deadline() -> None:
    clock = FakeClock()
    got = poll_for_turn(
        silence(), clock=clock.time, sleep=clock.sleep, timeout=2.0, poll_interval=0.5
    )
    assert got is None


def test_the_deadline_boundary_itself_counts_as_expired() -> None:
    """One convention for every time-bound in the peer, matching `Deadline`."""
    clock = FakeClock()
    poll_for_turn(
        silence(), clock=clock.time, sleep=clock.sleep, timeout=1.0, poll_interval=0.5
    )
    assert clock.now == 1.0  # stopped *at* the boundary, not past it


def test_it_never_sleeps_after_deciding_to_give_up() -> None:
    """A peer that oversleeps its own deadline has not really bounded anything."""
    clock = FakeClock()
    poll_for_turn(
        silence(), clock=clock.time, sleep=clock.sleep, timeout=1.0, poll_interval=0.5
    )
    assert sum(clock.slept) <= 1.0


def test_every_poll_iteration_emits_a_heartbeat() -> None:
    """Book 8.4.2: the watchdog watches the main loop, and this *is* the main loop."""
    clock = FakeClock()
    pulses: list[float] = []
    poll_for_turn(
        silence(),
        clock=clock.time,
        sleep=clock.sleep,
        timeout=1.0,
        poll_interval=0.5,
        heartbeat=lambda: pulses.append(clock.now),
    )
    assert pulses == [0.0, 0.5, 1.0]


def test_a_non_positive_poll_interval_is_refused() -> None:
    clock = FakeClock()
    with pytest.raises(PollingError, match="poll_interval"):
        poll_for_turn(
            silence(), clock=clock.time, sleep=clock.sleep, timeout=1.0, poll_interval=0
        )


def test_a_negative_timeout_is_refused() -> None:
    clock = FakeClock()
    with pytest.raises(PollingError, match="timeout"):
        poll_for_turn(silence(), clock=clock.time, sleep=clock.sleep, timeout=-1.0)


# `turn_receiver` -- the binding into run_turn's `Receive` -- is covered in
# tests/unit/test_turn_receiver.py, which reuses `FakeClock` from here.
