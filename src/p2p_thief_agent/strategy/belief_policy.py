"""Belief-driven Thief evasion: maximise distance from the believed Cop cell (`M6-004a`).

The perception layer yields a probability distribution over the Cop's position; this module
turns that into a legal move by reading off the most likely Cop cell and handing it to the
deterministic baseline policy as the threat. Reusing `choose_action` is deliberate — every
guarantee it already proves carries over unchanged:

- the move is **always legal** (`M6-004e`): `choose_action` only ever returns a legal
  action, so a belief that misdirects the Thief — even one peaked on a wall or on the
  Thief's own cell — can never produce an illegal move;
- the tie-breaks are **fixed** (`M6-004g`): identical inputs yield an identical action;
- nothing on this path is an LLM or a network call (`M6-004b`): the belief is a plain
  matrix of numbers and the policy is pure Python.

The belief is a `board.size × board.size` grid; cell `(r, c)` maps to board coordinate
`(min_index + r, min_index + c)`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError
from p2p_thief_agent.strategy.baseline import choose_action

Grid = Sequence[Sequence[float]]


def initial_belief(board: Board, cop_start: Coordinate) -> tuple[tuple[float, ...], ...]:
    """Belief before any observation: the Cop's public start cell is known certainty (`M6-021`).

    The agreed start positions are public, and this peer moves first, so on turn 1 the Cop is
    exactly at its start — a point mass, not a uniform guess. Later scent observations spread
    it as the Cop moves.
    """
    board.validate_position(cop_start)
    start = (cop_start.row - board.min_index, cop_start.col - board.min_index)
    return tuple(
        tuple(1.0 if (r, c) == start else 0.0 for c in range(board.size))
        for r in range(board.size)
    )


def believed_cop_cell(belief: Grid, board: Board) -> Coordinate:
    """Return the single most-likely Cop cell, breaking ties by lowest row then column.

    A distribution can be multimodal or flat; the tie-break makes the choice deterministic
    so the whole policy stays reproducible (`M6-004g`). The belief must match the board.
    """
    if len(belief) != board.size or any(len(row) != board.size for row in belief):
        raise DomainError(f"belief must be a {board.size}x{board.size} grid")
    row, col = max(
        ((r, c) for r in range(board.size) for c in range(board.size)),
        key=lambda rc: (belief[rc[0]][rc[1]], -rc[0], -rc[1]),
    )
    return Coordinate(board.min_index + row, board.min_index + col)


def choose_evasive_action(
    board: Board,
    position: Coordinate,
    belief: Grid,
    barriers: Iterable[Coordinate] = (),
) -> Action:
    """Return the best legal action, maximising distance from the believed Cop cell.

    The believed cell becomes the single threat fed to the baseline policy, so evasion,
    dead-end avoidance, and the fixed tie-break order all come from `choose_action`.
    """
    threat = believed_cop_cell(belief, board)
    return choose_action(board, position, police_positions=(threat,), barriers=barriers)
