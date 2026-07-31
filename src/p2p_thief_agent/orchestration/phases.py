"""The declared turn phase machine (`M5-007a`).

Appendix E rules 4 and 5 require game state to be managed as an explicit state
machine that **rejects** any transition outside its table. The value is not
bookkeeping: it converts a silent hang into a caught error, and it gives a mid-turn
disconnect one defined exit instead of a deadlock (`AE-006`, `AE-007`).

The table is transcribed from the specification's own listing, unchanged:

    WAITING_FOR_OPPONENT -> COMPUTING_MOVE
    COMPUTING_MOVE       -> COMMITTING | TECHNICAL_LOSS
    COMMITTING           -> AWAITING_REVEAL
    AWAITING_REVEAL      -> VERIFYING | TECHNICAL_LOSS
    VERIFYING            -> WAITING_FOR_OPPONENT
    TECHNICAL_LOSS       -> (terminal)

**What the names mean on this wire.** They come from the book's four-phase
commit-reveal. The simulator wire this repository speaks has **no live reveal**: a
turn message carries the hint, the scent grid, and the commitment hash, while the
move, the true position, the bluff verdict, and the nonce stay private until the
post-game audit (`C-022`). So `AWAITING_REVEAL` is the state of having committed and
being owed the opponent's next turn, and `VERIFYING` is checking what arrived. The
mandated names are kept verbatim rather than renamed to suit the carrier, because
rule 4 governs the declared machine, not our vocabulary.

`TECHNICAL_LOSS` is reachable only from the two phases the table permits — a peer
cannot abandon a turn it has not committed to. If that ever needs to change, the
table changes first.
"""

from __future__ import annotations

from enum import Enum


class Phase(Enum):
    """One declared state of a turn."""

    WAITING_FOR_OPPONENT = "WAITING_FOR_OPPONENT"
    COMPUTING_MOVE = "COMPUTING_MOVE"
    COMMITTING = "COMMITTING"
    AWAITING_REVEAL = "AWAITING_REVEAL"
    VERIFYING = "VERIFYING"
    TECHNICAL_LOSS = "TECHNICAL_LOSS"


TRANSITIONS: dict[Phase, frozenset[Phase]] = {
    Phase.WAITING_FOR_OPPONENT: frozenset({Phase.COMPUTING_MOVE}),
    Phase.COMPUTING_MOVE: frozenset({Phase.COMMITTING, Phase.TECHNICAL_LOSS}),
    Phase.COMMITTING: frozenset({Phase.AWAITING_REVEAL}),
    Phase.AWAITING_REVEAL: frozenset({Phase.VERIFYING, Phase.TECHNICAL_LOSS}),
    Phase.VERIFYING: frozenset({Phase.WAITING_FOR_OPPONENT}),
    Phase.TECHNICAL_LOSS: frozenset(),
}

# One full turn in the order the reference performs it.
TURN_CYCLE: tuple[Phase, ...] = (
    Phase.COMPUTING_MOVE,
    Phase.COMMITTING,
    Phase.AWAITING_REVEAL,
    Phase.VERIFYING,
    Phase.WAITING_FOR_OPPONENT,
)


class PhaseError(RuntimeError):
    """Raised when a transition is not in the declared table (`AE-005`)."""


class PhaseMachine:
    """Track this peer's turn phase, refusing every undeclared transition."""

    __slots__ = ("_history",)

    def __init__(self, start: Phase = Phase.WAITING_FOR_OPPONENT) -> None:
        if not isinstance(start, Phase):
            raise PhaseError(f"start must be a Phase, got {start!r}")
        self._history: list[Phase] = [start]

    @property
    def current(self) -> Phase:
        """Return the phase this peer is in now."""
        return self._history[-1]

    @property
    def history(self) -> tuple[Phase, ...]:
        """Return every phase entered, in order, including the starting one."""
        return tuple(self._history)

    @property
    def is_terminal(self) -> bool:
        """Return whether no transition out of the current phase exists."""
        return not TRANSITIONS[self.current]

    def to(self, phase: Phase) -> Phase:
        """Enter ``phase``, or raise naming the transition that was refused."""
        if not isinstance(phase, Phase):
            raise PhaseError(f"target must be a Phase, got {phase!r}")
        allowed = TRANSITIONS[self.current]
        if phase not in allowed:
            permitted = ", ".join(sorted(p.value for p in allowed)) or "nothing (terminal)"
            raise PhaseError(
                f"illegal transition {self.current.value} -> {phase.value}; allowed: {permitted}"
            )
        self._history.append(phase)
        return phase

    def fail(self) -> Phase:
        """Route a mid-turn fault to the one declared terminal state (`AE-007`)."""
        return self.to(Phase.TECHNICAL_LOSS)

    def complete_turn(self) -> tuple[Phase, ...]:
        """Walk one full turn cycle, returning the phases entered."""
        return tuple(self.to(phase) for phase in TURN_CYCLE)
