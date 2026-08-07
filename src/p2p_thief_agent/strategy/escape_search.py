"""Exact escape sets against a modelled deterministic pursuer (`M6-029`).

Against a *deterministic* pursuer the game has no chance and no hidden state, so
"can the Thief still reach the horizon from here?" is not a heuristic question — it
is a finite recursion over `(pursuer cell, thief cell, steps left)`, answerable
exactly. This module is that recursion. Seeded with the pursuer's true cell it is the
solver that produced the research report's ceiling row (24/24 escapable against all
three archetypes); seeded with the *believed* cell it becomes a legal agent's planner,
which is the whole difference between an instrument and a strategy.

One step follows the measurement harness's order (`test_strategy_comparison.simulate`):
the pursuer moves first from `(cop, thief)` — meeting the thief is capture — then the
thief moves, and stepping onto the pursuer is capture. `steps_left` counts full such
steps; reaching zero uncaught is the horizon, inclusive (`U-022`).

The recursion cannot cycle (`steps_left` strictly decreases) and its depth is the
horizon, far under the interpreter limit. Memoisation is the caller's dict, keyed
`(cop, thief, steps_left)`; the caller owns it because its validity is scoped to one
`(model, blocked)` pair — a new barrier invalidates every entry, and only the caller
knows when barriers changed. On the negotiated 7×7 the whole reachable table is a few
tens of thousands of states, milliseconds against the 30 s response budget.
"""

from __future__ import annotations

from collections.abc import Callable

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move

PursuerModel = Callable[[Board, Coordinate, Coordinate, frozenset], Coordinate]
Memo = dict[tuple[Coordinate, Coordinate, int], bool]


def survives(
    board: Board,
    model: PursuerModel,
    cop: Coordinate,
    thief: Coordinate,
    steps_left: int,
    blocked: frozenset[Coordinate],
    memo: Memo,
) -> bool:
    """Return whether the thief can reach the horizon from this state, exactly.

    ``True`` means an escape line exists against ``model`` played perfectly by both
    sides from here; ``False`` means every line ends in capture. The answer is exact
    *for the model* — a real opponent that differs from the model can of course
    diverge, which is why the adaptive policy scores models against observation before
    trusting one.
    """
    if steps_left <= 0:
        return True
    key = (cop, thief, steps_left)
    cached = memo.get(key)
    if cached is not None:
        return cached
    chased = model(board, cop, thief, blocked)
    outcome = False
    if chased != thief:
        for action in legal_actions(board, thief, blocked):
            target = resolve_move(board, thief, action, blocked)
            if target == chased:
                continue  # stepping onto the pursuer is capture, not escape
            if survives(board, model, chased, target, steps_left - 1, blocked, memo):
                outcome = True
                break
    memo[key] = outcome
    return outcome


def escape_actions(
    board: Board,
    model: PursuerModel,
    thief: Coordinate,
    cop: Coordinate,
    steps_after: int,
    blocked: frozenset[Coordinate],
    memo: Memo,
) -> tuple[Action, ...]:
    """Return every action that still guarantees the horizon against ``model``.

    Called at the thief's decision point, where the harness order says the pursuer
    has already moved this step: ``cop`` is its current cell, and ``steps_after`` is
    the number of full steps remaining *after* the move being chosen. The order of
    the returned actions is the domain's fixed declaration order, so downstream
    tie-breaks stay deterministic.
    """
    if steps_after < 0:
        raise ValueError(f"steps_after must be non-negative, got {steps_after}")
    winners = []
    for action in legal_actions(board, thief, blocked):
        target = resolve_move(board, thief, action, blocked)
        if target == cop:
            continue
        if survives(board, model, cop, target, steps_after, blocked, memo):
            winners.append(action)
    return tuple(winners)
