"""Deterministic walling pursuers the barrier-aware planner can plan against (`M6-034`).

The mover archetypes in `pursuer_models.py` only step, yet the book gives the Police a
barrier quota (Appendix F minimum 14): walling the Thief's cell captures, and a Thief whose
every exit is sealed is captured (`AE-046`, book §3.4 — verified from the book directly, the
Cop "may place a barrier one step away" and giving up its move to do so). A league opponent
that converts its quota into traps is the strongest realistic threat, and no mover model can
express it. This module is the walling archetype **in `src`** so a planner — not only a
`scripts/` grid — can search against it.

Semantics are byte-identical to `scripts/experiment_wallers._waller` (a parity test pins
this), lifted here unchanged so the planner assumes exactly the pursuer the grid measures:
finish (wall the Thief's cell when in range), else seal (wall an exit while the Thief has two
or fewer), else move via the wrapped mover. A wall forgoes the move that turn.

Wall candidates are the four cells orthogonally adjacent to the Police, in a fixed row-major
order — a strict subset of what `domain.barriers.validate_barrier_placement` permits (own-cell
placement is left out as an instrument simplification, as in the grid), so every wall this
proposes is a legal placement by construction; a test asserts it against the domain rule.

These are **instruments**: like the movers they read the Thief's true cell, so they are test
doubles and a planner's assumed opponent, never a live agent's input (`AE-8` binds agents, not
instruments). Pure and deterministic: no state, no randomness, ties on the fixed candidate
order — a planner assuming one gets exactly the pursuer the grid measured (`M6-004g`).
"""

from __future__ import annotations

from collections.abc import Callable

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.strategy.metrics import mobility
from p2p_thief_agent.strategy.pursuer_models import greedy_step, interceptor_step

# A walling pursuer returns (new_cop_cell, wall_cell_or_None). A wall forgoes the move, so the
# cop cell is unchanged when a wall is returned; None means the pursuer moved instead.
Mover = Callable[[Board, Coordinate, Coordinate, frozenset], Coordinate]
WallerModel = Callable[[Board, Coordinate, Coordinate, frozenset, int],
                       tuple[Coordinate, Coordinate | None]]

# Book §3.4 walling range, own-cell placement omitted as an instrument simplification (the
# same four cells, in the same order, the committed grid uses).
_WALL_DELTAS = ((-1, 0), (0, -1), (0, 1), (1, 0))
_SEAL_THRESHOLD = 2  # start sealing once the Thief has two or fewer exits


def wall_candidates(board: Board, cop: Coordinate, blocked: frozenset) -> list[Coordinate]:
    """The four in-range wall cells that are on-board and not already blocked, row-major."""
    cells = [Coordinate(cop.row + dr, cop.col + dc) for dr, dc in _WALL_DELTAS]
    return [cell for cell in cells if board.contains(cell) and cell not in blocked]


def walling_pursuer(mover: Mover) -> WallerModel:
    """Wrap a mover into a walling pursuer: finish, else seal, else chase (`M6-032` shape)."""

    def pursue(board: Board, cop: Coordinate, thief: Coordinate,
               blocked: frozenset, quota: int) -> tuple[Coordinate, Coordinate | None]:
        if quota > 0:
            candidates = wall_candidates(board, cop, blocked)
            for cell in candidates:
                if cell == thief:
                    return cop, cell  # a wall on the Thief's cell captures (§3.4)
            if mobility(board, thief, blocked) <= _SEAL_THRESHOLD:
                for cell in candidates:
                    if mobility(board, thief, blocked | {cell}) < mobility(board, thief, blocked):
                        return cop, cell  # seal an exit while it is scarce
        return mover(board, cop, thief, frozenset(blocked)), None

    return pursue


greedy_waller = walling_pursuer(greedy_step)
interceptor_waller = walling_pursuer(interceptor_step)

# Classification/tie-break order mirrors the mover ladder: assume the cheaper waller first.
WALLERS: dict[str, WallerModel] = {"greedy_waller": greedy_waller,
                                   "interceptor_waller": interceptor_waller}
