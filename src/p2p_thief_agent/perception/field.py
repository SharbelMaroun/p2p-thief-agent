"""Board-level scent: involuntary emission, and the bridge from an observed field to belief.

`scent.py` gives the 5×5 emission profile and the per-cell decay; this module lays that onto
the whole board. Two properties `M6-007` must prove live here by construction:

- **Emission is involuntary (`M6-007a`, `M6-007c`).** `deposit` takes the agent's *cell*,
  never its *action*, and carries no suppression flag. Every turn stamps the emission at
  wherever the agent stands — including a `STAY`, which lands on the same cell and emits
  again — so no branch and no path can skip or fake the trail.
- **Only the opponent's field is evidence (`M6-007b`).** `scent_likelihood` turns an
  *observed* field (the opponent's, parsed from the wire) into a likelihood for the belief
  update. The Thief's own `deposit` output is encoded outbound and is never passed here — a
  guard test proves the belief modules never touch the own-emission functions.

The board field is a `size × size` grid; index `(i, j)` is board coordinate
`(min_index + i, min_index + j)`.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.perception.belief import Grid, normalize
from p2p_thief_agent.perception.scent import advance_field, emission_delta

_RADIUS = 2  # the 5×5 window reaches two cells from the centre


def blank_field(board: Board) -> Grid:
    """Return an all-zero board scent field: every cell silent until something emits."""
    return tuple(tuple(0.0 for _ in range(board.size)) for _ in range(board.size))


def emit_at(board: Board, cell: Coordinate) -> Grid:
    """Return the board-sized emission Δτ centred on ``cell``, clipped to the board.

    Off-board parts of the 5×5 window are simply dropped. Takes only the cell, so there is
    no action to condition on and nothing to suppress (`M6-007c`).
    """
    board.validate_position(cell)
    centre_row, centre_col = cell.row - board.min_index, cell.col - board.min_index
    grid = [[0.0] * board.size for _ in range(board.size)]
    for d_row in range(-_RADIUS, _RADIUS + 1):
        for d_col in range(-_RADIUS, _RADIUS + 1):
            row, col = centre_row + d_row, centre_col + d_col
            if 0 <= row < board.size and 0 <= col < board.size:
                grid[row][col] = emission_delta(d_row, d_col)
    return tuple(tuple(row) for row in grid)


def deposit(field: Grid, board: Board, cell: Coordinate) -> Grid:
    """Advance the board field one turn: decay everywhere, then emit at ``cell``.

    Involuntary by construction — the agent's action never reaches this function, so a
    `STAY` deposits scent exactly as a move does (`M6-007a`).
    """
    return advance_field(field, emit_at(board, cell))


def scent_likelihood(observed: Mapping[tuple[int, int], float], board: Board) -> Grid:
    """Turn an observed (opponent) field into a belief likelihood over the grid (`M6-007b`).

    A cell's intensity is its evidence weight; an empty observation carries no information
    and normalises to uniform. Off-board cells are ignored — validated separately on parse.
    """
    grid = [[0.0] * board.size for _ in range(board.size)]
    for (row, col), intensity in observed.items():
        i, j = row - board.min_index, col - board.min_index
        if 0 <= i < board.size and 0 <= j < board.size:
            grid[i][j] = intensity
    return normalize(grid)
