"""One turn, driven by the declared phase machine (`M5-007`).

The reference's iteration order: **await the opponent, think, apply locally, seal,
send**. A peer must receive before advancing its own step, which is what makes the
exchange a strict alternation rather than two peers talking over each other.

**The Thief opens.** The book gives the first move of every turn cycle to the Thief,
and the Cop sees its hint before choosing — so on step 1 this peer does *not* wait.
That is a real asymmetry, not a flag for symmetry's sake: a Thief that waited first
would deadlock against a Cop correctly waiting for it.

Transport-neutral by construction: a `PeerTransport` and a `receive` callable are
passed in and no FastMCP symbol is imported, so a whole sub-game runs without a
socket and the same code runs over one.

**Atomicity.** A turn is sealed exactly once. If the send then fails the record is
not re-sealed — a commitment is a promise, and a second hash for the same step hands
the opponent an audit mismatch, which is an automatic zero for both sides `[AE-019]`.
The peer keeps the promise it made and takes the declared terminal exit.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from p2p_thief_agent.adapters.fastmcp_client import PeerRejectionError, TransportError
from p2p_thief_agent.orchestration.phases import Phase, PhaseMachine
from p2p_thief_agent.protocol.crypto import CryptoError
from p2p_thief_agent.protocol.wire import WireError

# Decide this turn: given the opponent's last message (None when this peer opens),
# return the public turn message to send and the sealed record to keep.
Decide = Callable[[dict | None, int], tuple[dict, dict]]
# Take the opponent's next turn message, or None if none arrived in time.
Receive = Callable[[], dict | None]
# Called with every phase entered, for the log manager (`M5-008`).
OnTransition = Callable[[Phase], None]


class TurnLoopError(RuntimeError):
    """Raised when a turn cannot complete and no phase transition covers it."""


@dataclass(frozen=True, slots=True)
class TurnRecord:
    """What one completed turn did, in enough detail to replay it."""

    step: int
    received: dict | None
    sent: dict
    sealed: dict
    phases: tuple[Phase, ...]


def run_turn(
    step: int,
    *,
    machine: PhaseMachine,
    transport: object,
    receive: Receive,
    decide: Decide,
    records: list[dict],
    opens: bool = False,
    on_transition: OnTransition | None = None,
) -> TurnRecord:
    """Run one turn through the phase machine and return what it did.

    ``records`` is this peer's private audit ledger; the sealed record is appended
    **once**, before the send, and never rewritten if delivery fails.
    """
    entered: list[Phase] = []

    def enter(phase: Phase) -> None:
        machine.to(phase)
        entered.append(phase)
        if on_transition is not None:
            on_transition(phase)

    incoming = None if opens else _await_opponent(machine, receive, enter)

    # Deciding and sealing both happen in COMPUTING_MOVE, because that is the only
    # phase from which the table permits TECHNICAL_LOSS. Entering COMMITTING means
    # the commitment already exists and must now go out: the table gives it exactly
    # one exit, so a peer cannot abandon a promise it has already made.
    enter(Phase.COMPUTING_MOVE)
    try:
        message, sealed = decide(incoming, step)
    except (WireError, CryptoError, ValueError) as exc:
        machine.fail()
        raise TurnLoopError(f"step {step} could not be sealed: {exc}") from exc

    enter(Phase.COMMITTING)
    records.append(sealed)

    enter(Phase.AWAITING_REVEAL)
    _deliver(step, message, transport, machine)

    enter(Phase.VERIFYING)
    enter(Phase.WAITING_FOR_OPPONENT)
    return TurnRecord(step, incoming, message, sealed, tuple(entered))


def _await_opponent(machine: PhaseMachine, receive: Receive, enter: OnTransition) -> dict:
    """Return the opponent's turn, or take the declared exit if none arrives.

    Silence is not patience: a peer that owes a turn and sends nothing ends the game
    rather than blocking it (`AE-007`).

    The two-step exit is forced by the table, not chosen — there is no
    ``WAITING_FOR_OPPONENT -> TECHNICAL_LOSS`` edge, so a starved peer must enter
    ``COMPUTING_MOVE`` first. Read strictly that is what the specification says; it
    may equally be a gap in the published table. It is followed as written, because
    inventing an edge would weaken the guarantee rule 5 exists for.
    """
    incoming = receive()
    if incoming is None:
        enter(Phase.COMPUTING_MOVE)
        machine.fail()
        raise TurnLoopError("opponent did not send a turn before the deadline")
    return incoming


def _deliver(step: int, message: dict, transport: object, machine: PhaseMachine) -> None:
    """Send the sealed turn, never re-sealing it, and route a failure cleanly.

    ``PeerRejectionError`` is a decided game outcome and ``TransportError`` a carrier
    fault. Both end the turn, but keeping them apart is what stops a lost game being
    retried forever as a network blip (`M5-010a`).
    """
    send = getattr(transport, "receive_turn", None)
    if send is None:
        raise TurnLoopError("transport does not expose receive_turn")
    try:
        send(message)
    except (TransportError, PeerRejectionError) as exc:
        machine.fail()
        raise TurnLoopError(f"step {step} was sealed but not delivered: {exc}") from exc


def sealed_steps(records: Mapping | list[dict]) -> tuple[int, ...]:
    """Return the steps this peer has committed to, in order."""
    return tuple(record["payload"]["step"] for record in records)


def is_sealed_once(records: list[dict], step: int) -> bool:
    """Return whether exactly one commitment exists for ``step``."""
    return sealed_steps(records).count(step) == 1
