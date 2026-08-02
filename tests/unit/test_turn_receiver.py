"""`M5-019`: `turn_receiver` -- binding a bounded wait into run_turn's `Receive`.

`poll_for_turn` is the wait itself (tests/unit/test_polling.py); this is the
adapter that hands `run_turn` the zero-argument callable it expects. The one
property worth its own file is that each call starts a **fresh** budget, because
getting that wrong is invisible until a long match dies on a turn that never got
its own allowance.
"""

from p2p_thief_agent.orchestration.polling import turn_receiver
from tests.unit.test_polling import FakeClock, queued, silence


def test_each_receive_call_gets_its_own_fresh_budget() -> None:
    """A slow opponent must not spend the next turn's allowance.

    Carrying one deadline across turns would let a fast exchange subsidise a slow
    one and eventually expire a turn that never had its own full budget.
    """
    clock = FakeClock()
    take = queued({"step": 1}, None, {"step": 2})  # type: ignore[arg-type]
    receive = turn_receiver(
        take, clock=clock.time, sleep=clock.sleep, timeout=1.0, poll_interval=0.5
    )
    assert receive() == {"step": 1}
    assert receive() == {"step": 2}


def test_the_receiver_reports_silence_as_none_so_the_loop_can_end_the_game() -> None:
    """`run_turn` turns this `None` into the declared exit to TECHNICAL_LOSS."""
    clock = FakeClock()
    receive = turn_receiver(
        silence(), clock=clock.time, sleep=clock.sleep, timeout=1.0, poll_interval=0.5
    )
    assert receive() is None


def test_the_receiver_still_pulses_while_it_waits() -> None:
    """The heartbeat must survive the binding, or a waiting peer looks frozen."""
    clock = FakeClock()
    pulses: list[float] = []
    receive = turn_receiver(
        silence(),
        clock=clock.time,
        sleep=clock.sleep,
        timeout=1.0,
        poll_interval=0.5,
        heartbeat=lambda: pulses.append(clock.now),
    )
    assert receive() is None
    assert pulses == [0.0, 0.5, 1.0]
