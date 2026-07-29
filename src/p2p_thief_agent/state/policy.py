"""Integrate the deterministic baseline policy with Thief-local state.

This layer binds the pure baseline strategy (`EXC-001`) to the immutable local state:
it reads the board, current position, and known barriers from the state, asks the
baseline for a ranking or a single action, and advances the state by the chosen action.
A plausible Police position is always an explicit argument -- never local truth -- so no
Cop-private information enters the state. Selection is deterministic: the same state and
the same plausible threats always yield the same action, which makes a run replayable.
"""

from __future__ import annotations

from collections.abc import Iterable

from p2p_thief_agent.domain.capture import is_captured
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.state.local_state import ThiefLocalState
from p2p_thief_agent.state.scoring import (
    DEFAULT_SURVIVAL_THRESHOLD,
    Outcome,
    resolve_outcome,
)
from p2p_thief_agent.strategy.baseline import choose_action, rank_actions


def rank_local_actions(
    state: ThiefLocalState, plausible_police: Iterable[Coordinate] = ()
) -> list[Action]:
    """Rank every legal action for the current state, best first."""
    return rank_actions(
        state.board, state.position, plausible_police, state.known_barriers.cells
    )


def choose_local_action(
    state: ThiefLocalState, plausible_police: Iterable[Coordinate] = ()
) -> Action:
    """Return the single best legal action for the current state."""
    return choose_action(
        state.board, state.position, plausible_police, state.known_barriers.cells
    )


def step_with_baseline(
    state: ThiefLocalState, plausible_police: Iterable[Coordinate] = ()
) -> ThiefLocalState:
    """Choose the baseline action and return the advanced local state."""
    return state.advance(choose_local_action(state, plausible_police))


def local_outcome(
    state: ThiefLocalState,
    police: Coordinate,
    *,
    survival_threshold: int = DEFAULT_SURVIVAL_THRESHOLD,
    technical_loss: bool = False,
) -> Outcome | None:
    """Classify the current state's terminal outcome against a Police position.

    The Police position is an explicit auditable input, never stored in local state.
    Returns None while the sub-game is still in progress.
    """
    captured = is_captured(state.board, state.position, police, state.known_barriers.cells)
    return resolve_outcome(
        captured=captured,
        steps=state.step,
        survival_threshold=survival_threshold,
        technical_loss=technical_loss,
    )
