"""Pure positional metrics used to rank candidate Thief moves.

Every metric takes explicit board, barrier, and position inputs, holds no Cop-private
truth, performs no networking or external call, and depends on no shared-contract byte.
Distances use the Manhattan metric because movement is four-connected orthogonal
stepping (`AF-015`); the metric is therefore independent of the configured origin
corner, exactly like `board.orthogonal_neighbors`.
"""

from __future__ import annotations

from collections.abc import Iterable

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import cardinal_moves, resolve_move


def manhattan_distance(source: Coordinate, target: Coordinate) -> int:
    """Return the four-connected step distance between two cells."""
    return abs(source.row - target.row) + abs(source.col - target.col)


def min_threat_distance(cell: Coordinate, threats: Iterable[Coordinate]) -> int | None:
    """Return the distance to the nearest plausible threat, or None when none are known.

    A `None` result means the criterion is vacuous and must not influence ranking; it
    is never treated as distance zero.
    """
    distances = [manhattan_distance(cell, threat) for threat in threats]
    return min(distances) if distances else None


def mobility(board: Board, cell: Coordinate, barriers: Iterable[Coordinate] = ()) -> int:
    """Count the legal one-step escapes from a cell, excluding STAY.

    STAY is excluded deliberately: it is always legal but is not an escape, and a cell
    whose cardinal neighbours are all off-board or barriered is a capture (`AE-046`).
    """
    return len(cardinal_moves(board, cell, barriers))


def _reachable_neighbours(
    board: Board, cell: Coordinate, barriers: Iterable[Coordinate]
) -> list[Coordinate]:
    """Return the cells legally reachable in one cardinal step from a cell."""
    blocked = frozenset(barriers)
    return [
        resolve_move(board, cell, action, blocked)
        for action in cardinal_moves(board, cell, blocked)
    ]


def onward_reach(board: Board, cell: Coordinate, barriers: Iterable[Coordinate] = ()) -> int:
    """Sum the mobility of every cell reachable in one cardinal step.

    This is the two-ply breadth measure that distinguishes a genuine bottleneck from a
    cell that merely looks open: a corridor mouth has ordinary one-step mobility but
    little onward breadth.
    """
    blocked = frozenset(barriers)
    return sum(mobility(board, neighbour, blocked) for neighbour in _reachable_neighbours(board, cell, blocked))


def edge_contacts(board: Board, cell: Coordinate) -> int:
    """Count how many of the two axes sit on a board boundary.

    Returns 2 for a corner, 1 for a non-corner edge cell, and 0 for an interior cell.
    """
    on_row_edge = cell.row in (board.min_index, board.max_index)
    on_col_edge = cell.col in (board.min_index, board.max_index)
    return int(on_row_edge) + int(on_col_edge)


def one_wall_trap(
    board: Board,
    target: Coordinate,
    believed_cop: Coordinate,
    barriers: Iterable[Coordinate] = (),
) -> bool:
    """Return whether one legal Police wall next turn could finish a thief on ``target``.

    The Police may spend a turn walling its own cell or one orthogonal step from it
    (book §3.4), and a walled current cell or a fully sealed cell is a capture
    (`AE-046`). So a target adjacent to the believed Police whose escape count a
    single in-range wall reduces to zero — or the target cell itself being in walling
    range — is a cell where surviving next turn depends on the opponent declining a
    winning move. The check is exact for the rule, not a heuristic: it enumerates
    every in-range wall and asks whether any ends the game.
    """
    return wall_pressure(board, target, believed_cop, barriers) == 0


def wall_pressure(
    board: Board,
    target: Coordinate,
    believed_cop: Coordinate,
    barriers: Iterable[Coordinate] = (),
) -> int:
    """Return the exits ``target`` keeps after the believed Police's best single wall.

    ``0`` is `one_wall_trap`'s condition — the next wall (or a wall on the target
    itself) ends the game. ``1`` is the seal cascade the waller grid measured: a
    two-exit corner loses one exit, the survivor is the only move left, and the wall
    after that finishes it — so the refusal has to fire a step before the trap is
    literal. Out of walling range the answer is simply the current mobility.
    """
    blocked = frozenset(barriers)
    reach = [believed_cop, *_reachable_neighbours(board, believed_cop, blocked)]
    if target in reach:
        return 0  # a wall on our own cell is an immediate capture
    worst = mobility(board, target, blocked)
    for wall in reach:
        worst = min(worst, mobility(board, target, blocked | {wall}))
    return worst
