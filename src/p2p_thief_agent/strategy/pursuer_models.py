"""Deterministic pursuer archetypes the evasion can plan against (`M6-029`).

The research report's stronger-Cop rows — herding 23/24, anticipating **8/24** — were
measured with session-scratch code that was never committed: the archetypes existed as
table numbers and nowhere else, so neither the measurements nor any counter-strategy
could be reproduced. These are the three pursuers as code, shared by the measurement
grid (`scripts/experiment_pursuers.py`) and the adaptive policy, which plans against
exactly the models the grid measures.

The reference simulator predicts nothing — asked directly (2026-08-08), its brains are
"deliberately simple" greedy heuristics chasing the current believed cell, and students
are "expected to upgrade the strategy". So **greedy** is the reference-shaped opponent
and the likeliest league default; **herding** is its cheapest tie-break refinement; and
**anticipating** — aim at the centroid of the Thief's next legal cells — is the
cheapest genuine upgrade a classmate is likely to ship, and the one that collapses our
escape rate. The companion repository's opponent grid climbs the same ladder from the
other side of the board.

Every model is a pure function `(board, cop, thief, blocked) -> Coordinate`: no state,
no randomness, ties broken on the fixed action token order, so a planner that assumes
one of these gets exactly the pursuer the grid measured (`M6-004g` discipline). They
model *pursuers*, so they read the Thief's true cell — these are instruments and test
doubles, never a live agent's inputs (`AE-8` binds agents, not instruments).
"""

from __future__ import annotations

from collections.abc import Iterable

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.metrics import manhattan_distance

_NO_BARRIERS: frozenset[Coordinate] = frozenset()


def _targets(board: Board, cop: Coordinate, blocked: frozenset) -> dict[Action, Coordinate]:
    return {action: resolve_move(board, cop, action, blocked)
            for action in legal_actions(board, cop, blocked)}


def _flight(board: Board, thief: Coordinate, blocked: frozenset) -> tuple[Coordinate, ...]:
    """The thief's current cell and every cell one legal step away from it."""
    return (thief, *(resolve_move(board, thief, action, blocked)
                     for action in legal_actions(board, thief, blocked)
                     if action is not Action.STAY))


def greedy_step(
    board: Board,
    cop: Coordinate,
    thief: Coordinate,
    blocked: Iterable[Coordinate] = _NO_BARRIERS,
) -> Coordinate:
    """The reference shape: minimise Manhattan distance to the thief's current cell.

    Byte-for-byte the harness Cop of `test_strategy_comparison._cop_pursues`, kept in
    one place so the grid, the solver, and the tracker all chase with the same brain.
    """
    targets = _targets(board, cop, frozenset(blocked))
    return targets[min(targets,
                       key=lambda a: (manhattan_distance(targets[a], thief), a.value))]


def herding_step(
    board: Board,
    cop: Coordinate,
    thief: Coordinate,
    blocked: Iterable[Coordinate] = _NO_BARRIERS,
) -> Coordinate:
    """Closes like greedy, but breaks distance ties to shrink the thief's room.

    Room is the thief's onward options that still *gain* ground from the tie cell:
    among equally close moves the pursuer prefers the one leaving the thief the fewest
    flight cells strictly farther away than it stands now.
    """
    blocked = frozenset(blocked)
    targets = _targets(board, cop, blocked)

    def room(target: Coordinate) -> int:
        here = manhattan_distance(target, thief)
        return sum(1 for cell in _flight(board, thief, blocked)
                   if manhattan_distance(target, cell) > here)

    return targets[min(targets, key=lambda a: (manhattan_distance(targets[a], thief),
                                               room(targets[a]), a.value))]


def anticipating_step(
    board: Board,
    cop: Coordinate,
    thief: Coordinate,
    blocked: Iterable[Coordinate] = _NO_BARRIERS,
) -> Coordinate:
    """Chase the centroid of the thief's next legal cells, not the thief itself.

    The upgrade that cut the shipped evasion from 23/24 to 8/24: running from where
    the pursuer *is* is exactly what aiming where the runner *can go* exploits. The
    centroid is usually fractional; the comparison is kept in integers by scaling both
    axes by the flight-set size, so no float ever orders a move (`M6-004g`).
    """
    blocked = frozenset(blocked)
    cells = _flight(board, thief, blocked)
    scale, row_sum = len(cells), sum(cell.row for cell in cells)
    col_sum = sum(cell.col for cell in cells)
    targets = _targets(board, cop, blocked)

    def lead(target: Coordinate) -> int:
        return abs(target.row * scale - row_sum) + abs(target.col * scale - col_sum)

    return targets[min(targets, key=lambda a: (lead(targets[a]),
                                               manhattan_distance(targets[a], thief),
                                               a.value))]


def _step_distances(
    board: Board, origin: Coordinate, blocked: frozenset
) -> dict[Coordinate, int]:
    """Barrier-aware breadth-first step counts from ``origin``; unreachable is absent."""
    distances = {origin: 0}
    frontier = [origin]
    while frontier:
        cell = frontier.pop(0)
        for action in legal_actions(board, cell, blocked):
            if action is Action.STAY:
                continue
            neighbour = resolve_move(board, cell, action, blocked)
            if neighbour not in distances:
                distances[neighbour] = distances[cell] + 1
                frontier.append(neighbour)
    return distances


def interceptor_step(
    board: Board,
    cop: Coordinate,
    thief: Coordinate,
    blocked: Iterable[Coordinate] = _NO_BARRIERS,
) -> Coordinate:
    """Close on the whole flight set by summed true step distance, spread included.

    The centroid chaser collapses the flight set to its mean, so a runner bobbing on
    a pinned axis ties it and the tie-break dances. Summing barrier-aware distances
    to *every* flight cell prices the spread — the strongest mover shape a strong
    classmate can cheaply ship, so the planner must be able to assume it. An
    unreachable flight cell prices as one full board: conceded ground, not ignored.
    """
    blocked = frozenset(blocked)
    cells = _flight(board, thief, blocked)
    fields = [_step_distances(board, cell, blocked) for cell in cells]
    far = board.size * board.size + 1
    targets = _targets(board, cop, blocked)

    def race(target: Coordinate) -> tuple[int, int]:
        steps = [field.get(target, far) for field in fields]
        return (sum(steps), max(steps))

    return targets[min(targets, key=lambda a: (*race(targets[a]), a.value))]


# Classification order is also the tie-break order: on equal evidence assume the
# simplest pursuer, which is the reference shape a classmate most likely runs.
PURSUERS = {"greedy": greedy_step, "herding": herding_step,
            "anticipating": anticipating_step, "interceptor": interceptor_step}
