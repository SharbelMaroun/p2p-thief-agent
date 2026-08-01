"""Drive the passive mailbox, so a peer can play a match unattended (`M5-019`).

`adapters.build_server` is a *mailbox*: its four tools enqueue the opponent's
message and acknowledge it, and nothing inside them advances the game. `run_turn`
needs the opposite -- a `Receive` that yields the opponent's next turn or gives
up. This module is that bridge, and it is what turns a harness fed by hand into a
peer that plays on its own.

**Poll to drain; the state machine still decides.** The reference drives its
runtime by polling its *own* inboxes at `[network].poll_interval_seconds` (0.5 s
in the shipped config), while the book mandates a strict state machine gating
every transition (section 8.3). Both hold here, because they answer different
questions: polling is only *how* a queued message is picked up, and `PhaseMachine`
still decides what may legally happen next. A message that arrives out of turn is
refused by the transition table, never by this loop.

**Silence is bounded, never patient.** Appendix E rule 6 makes a deadline
mandatory "to prevent deadlocks while waiting for the opponent", so the wait stops
at the turn timeout and returns `None` -- which `run_turn` turns into the declared
exit to `TECHNICAL_LOSS`. Blocking forever is precisely the failure this prevents
`[AE-006]`.

**The heartbeat is emitted here, and that is the point.** Book section 8.4.2 puts
the watchdog on "the main game loop", and a peer waiting for an opponent is
otherwise doing nothing observable -- exactly the window where a frozen process
and a patient one look identical. So every poll iteration pulses, and a peer
asleep inside this loop still proves it is alive `[AE-007]`.

**Thief-specific note.** The Thief *opens* every cycle, so unlike the Cop its
step 1 never waits. That makes this module load-bearing from step 2 onward rather
than step 1 -- but no less load-bearing, because every later step still depends on
finding the Cop's answer in the mailbox.

Time is injected, so a timeout is proven by advancing a number rather than by
sleeping.
"""

from __future__ import annotations

from collections.abc import Callable

from p2p_thief_agent.peer.transport import JsonObject

# Pull the next already-validated opponent turn, or None if none is queued right
# now. Must never block: the waiting is this module's job, not the source's.
TakeTurn = Callable[[], JsonObject | None]
Clock = Callable[[], float]
Sleep = Callable[[float], None]
Heartbeat = Callable[[], None]

# How often to look in the mailbox. Local, private, and never negotiated: it
# changes only how quickly this peer notices a message that has already arrived,
# so it cannot affect interoperability or a hash. 0.5 s is the reference's
# shipped `[network].poll_interval_seconds`; the book publishes the key in its
# page-131 skeleton without fixing a value.
DEFAULT_POLL_INTERVAL = 0.5


class PollingError(ValueError):
    """Raised when a polling bound is not usable."""


def poll_for_turn(
    take: TakeTurn,
    *,
    clock: Clock,
    sleep: Sleep,
    timeout: float,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    heartbeat: Heartbeat | None = None,
) -> JsonObject | None:
    """Wait for the opponent's next turn; return `None` once the deadline passes.

    The mailbox is checked **before** the clock, so a turn already sitting in the
    queue is taken even when the budget is zero: the deadline exists to bound
    *waiting*, and refusing a message that has already arrived would forfeit a
    match on a technicality.

    The boundary itself counts as expired, matching `services.deadlines` -- one
    convention for every time-bound in the peer, so "expired" never means two
    different things.
    """
    if poll_interval <= 0:
        raise PollingError(f"poll_interval must be positive, got {poll_interval!r}")
    if timeout < 0:
        raise PollingError(f"timeout must not be negative, got {timeout!r}")

    deadline = clock() + timeout
    while True:
        if heartbeat is not None:
            heartbeat()
        message = take()
        if message is not None:
            return message
        if clock() >= deadline:
            return None
        sleep(poll_interval)


def turn_receiver(
    take: TakeTurn,
    *,
    clock: Clock,
    sleep: Sleep,
    timeout: float,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    heartbeat: Heartbeat | None = None,
) -> Callable[[], JsonObject | None]:
    """Bind a polling wait into the zero-argument `Receive` `run_turn` expects.

    Each call starts a fresh budget, because the timeout bounds *one* wait for
    *one* turn; carrying a deadline across turns would make a fast opponent
    subsidise a slow one and eventually expire a turn that never got its own full
    allowance.
    """

    def receive() -> JsonObject | None:
        return poll_for_turn(
            take,
            clock=clock,
            sleep=sleep,
            timeout=timeout,
            poll_interval=poll_interval,
            heartbeat=heartbeat,
        )

    return receive
