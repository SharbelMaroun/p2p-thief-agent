"""Deterministic contract-independent Thief baseline policy.

The policy ranks the legal actions by strict criterion priority and never by a weighted
sum, so every choice is explainable and no numeric weight needs calibration data:

1. discard any action whose target is a dead end (immediately trapping);
2. maximize the distance to the nearest plausible Police cell;
3. maximize one-step mobility at the target;
4. maximize two-ply onward reach, then minimize corner/edge contact;
5. break remaining ties by the fixed `Action` order (N, S, E, W, STAY).

Criterion 4 expands "corner and bottleneck penalty" into its two measurable parts:
`onward_reach` detects corridors and dangerous barrier layouts, `edge_contacts`
detects corners and edges.

A target counts as a dead end when every cell still reachable from it is the cell the
Thief just left. Plain "no escape at all" would be nearly vacuous here, because the
cell just vacated is always a legal way back, so a one-step target can never be fully
enclosed. A pocket whose only exit is backwards is the real immediate trap risk: the
Police can seal it on the following turn.

The policy is pure. It takes board, position, plausible threats, and disclosed
barriers explicitly; it performs no networking, no GUI work, and no external or LLM
call; it reads no Cop-private truth; it defines no new game rule; and it depends on no
shared-contract byte. It always returns an action that the domain accepts as legal.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import cardinal_moves, legal_actions, resolve_move
from p2p_thief_agent.strategy.metrics import (
    edge_contacts,
    min_threat_distance,
    mobility,
    onward_reach,
)

# Fixed deterministic tie-break order: the declaration order of Action.
_ACTION_ORDER: tuple[Action, ...] = tuple(Action)


def is_dead_end(
    board: Board,
    target: Coordinate,
    origin: Coordinate,
    barriers: Iterable[Coordinate] = (),
) -> bool:
    """Return whether every remaining exit from a target leads back to the origin.

    A fully enclosed target has no exits at all, which also counts as a dead end.
    """
    blocked = frozenset(barriers)
    exits = [
        resolve_move(board, target, action, blocked)
        for action in cardinal_moves(board, target, blocked)
    ]
    return all(cell == origin for cell in exits)


def _candidate_key(
    board: Board,
    target: Coordinate,
    action: Action,
    threats: Sequence[Coordinate],
    barriers: frozenset[Coordinate],
) -> tuple[int, int, int, int, int]:
    """Build the ascending lexicographic sort key for one candidate action.

    Maximized criteria are negated so that a single ascending sort expresses the whole
    priority order. A vacuous threat criterion contributes a constant, which leaves the
    remaining criteria to decide rather than pretending every cell is threatened.
    """
    nearest = min_threat_distance(target, threats)
    threat_rank = 0 if nearest is None else -nearest
    return (
        threat_rank,
        -mobility(board, target, barriers),
        -onward_reach(board, target, barriers),
        edge_contacts(board, target),
        _ACTION_ORDER.index(action),
    )


def rank_actions(
    board: Board,
    position: Coordinate,
    police_positions: Iterable[Coordinate] = (),
    barriers: Iterable[Coordinate] = (),
) -> list[Action]:
    """Return every legal action, best first, under the lexicographic criteria.

    Dead-end actions are ranked last as a block rather than dropped: they remain legal,
    so a caller facing nothing but dead ends still receives a complete legal ordering.
    That block ordering is the deterministic fallback.
    """
    board.validate_position(position)
    blocked = frozenset(barriers)
    threats = tuple(police_positions)
    legal = legal_actions(board, position, blocked)
    targets = {action: resolve_move(board, position, action, blocked) for action in legal}
    return sorted(
        legal,
        key=lambda action: (
            is_dead_end(board, targets[action], position, blocked),
            _candidate_key(board, targets[action], action, threats, blocked),
        ),
    )


def choose_action(
    board: Board,
    position: Coordinate,
    police_positions: Iterable[Coordinate] = (),
    barriers: Iterable[Coordinate] = (),
) -> Action:
    """Return the single best legal action for the Thief.

    `STAY` is always legal from an on-board cell, so a legal action always exists and
    this never raises for an on-board position. An off-board position is rejected by
    the domain rather than silently repaired.
    """
    return rank_actions(board, position, police_positions, barriers)[0]
