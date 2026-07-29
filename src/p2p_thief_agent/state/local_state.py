"""Immutable Thief-local game state with an append-only history.

The state records only Thief-local truth: the Thief's own position, the step count, the
barriers it has been told about, and immutable snapshots of every prior step. It never
stores the Police position or any Cop-private truth; a plausible Police position is
supplied explicitly to the strategy layer instead. Every transition returns a new state
and leaves the original untouched, so a history is an append-only chain of snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError, _validate_index
from p2p_thief_agent.domain.movement import resolve_move
from p2p_thief_agent.state.known_barriers import KnownBarriers


@dataclass(frozen=True, slots=True)
class ThiefSnapshot:
    """An immutable point-in-time record of Thief-local truth."""

    step: int
    position: Coordinate
    known_barriers: KnownBarriers
    action: Action | None


@dataclass(frozen=True, slots=True)
class ThiefLocalState:
    """Immutable Thief-local state; transitions return a new state."""

    board: Board
    position: Coordinate
    known_barriers: KnownBarriers = field(default_factory=KnownBarriers)
    step: int = 0
    last_action: Action | None = None
    history: tuple[ThiefSnapshot, ...] = ()

    def __post_init__(self) -> None:
        """Validate the current position and step against the board."""
        self.board.validate_position(self.position)
        _validate_index("step", self.step)
        if self.step < 0:
            raise DomainError(f"step must be nonnegative, got {self.step}")

    def snapshot(self) -> ThiefSnapshot:
        """Return the immutable snapshot of the current step."""
        return ThiefSnapshot(
            step=self.step,
            position=self.position,
            known_barriers=self.known_barriers,
            action=self.last_action,
        )

    def trajectory(self) -> tuple[ThiefSnapshot, ...]:
        """Return every snapshot in order, the current step last."""
        return self.history + (self.snapshot(),)

    def record_barrier(self, cell: Coordinate, *, step: int | None = None) -> ThiefLocalState:
        """Return a new state that also knows a barrier disclosed at a step.

        The disclosure defaults to the current step. Recording does not advance the
        turn, so no history snapshot is pushed; provenance lives in the barrier record.
        """
        disclosed = self.step if step is None else step
        updated = self.known_barriers.record(self.board, cell, step=disclosed)
        return replace(self, known_barriers=updated)

    def advance(self, action: Action) -> ThiefLocalState:
        """Apply one legal action, returning the next state and recording history.

        The move is resolved by the domain against the known barriers, so an illegal
        or off-board action raises rather than being silently repaired. The current
        snapshot is appended to the history of the returned state.
        """
        target = resolve_move(self.board, self.position, action, self.known_barriers.cells)
        return replace(
            self,
            position=target,
            step=self.step + 1,
            last_action=action,
            history=self.history + (self.snapshot(),),
        )
