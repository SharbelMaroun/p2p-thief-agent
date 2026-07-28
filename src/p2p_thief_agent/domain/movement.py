"""Legal movement: one orthogonal step or STAY, barrier-aware and deterministic.

Direction labels (N/S/E/W) resolve to row/column deltas per the configured origin
corner. Off-board and barriered targets are illegal (`AF-015`). Movement takes board
and barrier inputs explicitly and never reads Cop-private truth.
"""

from __future__ import annotations

from collections.abc import Iterable

from p2p_thief_agent.domain.board import Board, OriginCorner
from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError

_TOP_ORIGINS = (OriginCorner.TOP_LEFT, OriginCorner.TOP_RIGHT)
_LEFT_ORIGINS = (OriginCorner.TOP_LEFT, OriginCorner.BOTTOM_LEFT)


def _deltas(origin: OriginCorner) -> dict[Action, tuple[int, int]]:
    """Return per-action (row, col) deltas for the origin convention."""
    north_row = -1 if origin in _TOP_ORIGINS else 1
    east_col = 1 if origin in _LEFT_ORIGINS else -1
    return {
        Action.NORTH: (north_row, 0),
        Action.SOUTH: (-north_row, 0),
        Action.EAST: (0, east_col),
        Action.WEST: (0, -east_col),
        Action.STAY: (0, 0),
    }


def resolve_move(
    board: Board,
    position: Coordinate,
    action: Action,
    barriers: Iterable[Coordinate] = (),
) -> Coordinate:
    """Return the legal resulting cell for an action, else raise a domain error."""
    board.validate_position(position)
    blocked = frozenset(barriers)
    if action is Action.STAY:
        return position
    drow, dcol = _deltas(board.origin_corner)[action]
    target = Coordinate(position.row + drow, position.col + dcol)
    if not board.contains(target):
        raise DomainError(f"action {action.value} leaves the board")
    if target in blocked:
        raise DomainError(f"action {action.value} is blocked by a barrier")
    return target


def legal_actions(
    board: Board,
    position: Coordinate,
    barriers: Iterable[Coordinate] = (),
) -> list[Action]:
    """Enumerate legal actions in fixed Action order (deterministic)."""
    board.validate_position(position)
    blocked = frozenset(barriers)
    legal: list[Action] = []
    for action in Action:
        try:
            resolve_move(board, position, action, blocked)
        except DomainError:
            continue
        legal.append(action)
    return legal


def cardinal_moves(
    board: Board,
    position: Coordinate,
    barriers: Iterable[Coordinate] = (),
) -> list[Action]:
    """Enumerate only legal N/S/E/W steps, excluding STAY (used for trapping)."""
    return [action for action in legal_actions(board, position, barriers) if action is not Action.STAY]
