"""M5-019e: start-order tolerance -- waiting for an opponent that is not up yet.

Two peers launched by two people cannot start at the same instant, and the reference
is explicit that "start order doesn't matter". The subtlety worth testing is that this
is the *one* place patience is correct: everywhere else in the peer, waiting past a
deadline is a technical loss. Before the game exists there is nothing to forfeit.

It must still be bounded, and it must not raise -- an absent opponent is an operator
situation, not a protocol fault.
"""

import pytest

from p2p_thief_agent.services.readiness import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_RETRY_INTERVAL,
    ReadinessError,
    timeouts_from_private_config,
    wait_for_peer,
)
from tests.unit.test_polling import FakeClock


def up_after(attempts: int):
    """A probe that answers only from the nth attempt onward."""
    seen = {"n": 0}

    def probe() -> bool:
        seen["n"] += 1
        return seen["n"] > attempts

    return probe


def test_an_opponent_already_up_is_found_without_waiting() -> None:
    clock = FakeClock()
    assert wait_for_peer(lambda: True, clock=clock.time, sleep=clock.sleep) is True
    assert clock.slept == []


def test_an_opponent_already_up_is_found_even_with_no_budget() -> None:
    """The probe runs before the clock, so a zero budget still notices a live peer."""
    clock = FakeClock()
    assert wait_for_peer(
        lambda: True, clock=clock.time, sleep=clock.sleep, timeout=0.0
    ) is True


def test_a_peer_that_starts_late_is_waited_for() -> None:
    """The whole point: the other person can launch their peer after ours."""
    clock = FakeClock()
    got = wait_for_peer(
        up_after(3), clock=clock.time, sleep=clock.sleep, timeout=60.0, interval=1.0
    )
    assert got is True
    assert clock.slept == [1.0, 1.0, 1.0]


def test_an_opponent_that_never_starts_gives_up_and_says_so() -> None:
    """Waiting forever is a hang with no signal to the operator, not patience."""
    clock = FakeClock()
    got = wait_for_peer(
        lambda: False, clock=clock.time, sleep=clock.sleep, timeout=3.0, interval=1.0
    )
    assert got is False
    assert clock.now == 3.0


def test_giving_up_returns_false_rather_than_raising() -> None:
    """An absent opponent is an operator situation, not a protocol fault.

    Raising here would blur it with the in-match failures that really are faults,
    and rule 6's deadline must keep meaning something sharper than "nobody
    launched the other process yet".
    """
    clock = FakeClock()
    assert wait_for_peer(
        lambda: False, clock=clock.time, sleep=clock.sleep, timeout=1.0
    ) is False


def test_a_non_positive_interval_is_refused() -> None:
    clock = FakeClock()
    with pytest.raises(ReadinessError, match="interval"):
        wait_for_peer(lambda: False, clock=clock.time, sleep=clock.sleep, interval=0)


def test_a_negative_timeout_is_refused() -> None:
    clock = FakeClock()
    with pytest.raises(ReadinessError, match="timeout"):
        wait_for_peer(lambda: False, clock=clock.time, sleep=clock.sleep, timeout=-1.0)


def test_the_reference_defaults_are_the_shipped_ones() -> None:
    """60 s total, 1 s between tries -- confirmed against the reference 2026-08-02."""
    assert DEFAULT_CONNECT_TIMEOUT == 60.0
    assert DEFAULT_RETRY_INTERVAL == 1.0


def test_timeouts_are_read_from_the_private_network_section() -> None:
    config = {"network": {"connect_timeout_seconds": 5, "retry_interval_seconds": 0.25}}
    assert timeouts_from_private_config(config) == (5.0, 0.25)


def test_missing_timeout_keys_fall_back_to_the_defaults() -> None:
    """Safe to default precisely because neither value can change a match outcome."""
    assert timeouts_from_private_config({"network": {}}) == (60.0, 1.0)
    assert timeouts_from_private_config({}) == (60.0, 1.0)
