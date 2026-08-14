"""Exact escape sets against a modelled deterministic *walling* pursuer (`M6-034`).

`escape_search.survives` answers "can the Thief still reach the horizon?" against a pursuer
that only **moves** — barriers are frozen for the whole recursion. That is precisely the gap
a walling opponent exploits: it spends turns sealing the board, and a line planned as if the
walls never come walks into the trap they build. This module closes that gap by carrying the
barrier field and the remaining quota *inside* the recursion, so the pursuer's turn is a
choice between moving and walling exactly as the live game allows.

Because the modelled waller is **deterministic** (`strategy/waller_models.py`) there is no
branching on the pursuer's side — each node has one forced (move-or-wall) reply — so the tree
is the Thief's ≤5 actions deep, the same shape `escape_search` searches, plus a growing
barrier mask in the memo key. One step follows the committed waller grid's order exactly
(`scripts/experiment_wallers.play_walled`): the pursuer acts first (a wall on the Thief's cell,
the pursuer reaching the Thief's cell, or the Thief left with no exit is capture), then the
Thief moves (stepping onto the pursuer, or into a cell with no exit, is capture). Reaching
`steps_left == 0` uncaught is survival of the searched window.

The horizon is **bounded** by the caller (a receding window), because with the barrier mask in
the key the exact-to-horizon table is larger than the mover solver's: passing
`steps_left = min(remaining, cap)` keeps the cost inside the response budget while staying
exact for the endgame, where `remaining <= cap`. Memoisation is the caller's dict keyed
`(cop, thief, blocked, quota, steps_left)`; its validity is scoped to one waller model, so a
new model needs a fresh memo. Deterministic and history-free, so identical states give
identical answers — what the determinism tests pin and the audit leaves free.
"""

from __future__ import annotations

from collections.abc import Callable

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.metrics import mobility

WallerModel = Callable[[Board, Coordinate, Coordinate, frozenset, int],
                       tuple[Coordinate, Coordinate | None]]
WalledMemo = dict[tuple[Coordinate, Coordinate, frozenset, int, int], bool]


def _pursuer_reply(
    board: Board, waller: WallerModel, cop: Coordinate, thief: Coordinate,
    blocked: frozenset, quota: int,
) -> tuple[Coordinate | None, frozenset, int]:
    """Apply the waller's forced move-or-wall. Returns (cop, blocked, quota), or a capture.

    A ``None`` cop signals the pursuer's own action already captured the Thief this step — a
    wall on the Thief's cell, or the pursuer reaching it — so no Thief move follows.
    """
    new_cop, wall = waller(board, cop, thief, blocked, quota)
    if wall is not None:
        if wall == thief:
            return None, blocked, quota  # barrier-on-Thief capture (§3.4)
        return cop, blocked | {wall}, quota - 1  # a wall forgoes the move
    if new_cop == thief:
        return None, blocked, quota  # same-cell capture
    return new_cop, blocked, quota


def survives_walled(
    board: Board, waller: WallerModel, cop: Coordinate, thief: Coordinate,
    steps_left: int, blocked: frozenset, quota: int, memo: WalledMemo,
) -> bool:
    """Return whether the Thief survives ``steps_left`` steps against ``waller``, exactly.

    Exact *for the model*: a real opponent that differs from the assumed waller can diverge,
    which is why the caller only trusts this within a danger gate and keeps the shipped policy
    as the fallback.
    """
    if steps_left <= 0:
        return True
    key = (cop, thief, blocked, quota, steps_left)
    cached = memo.get(key)
    if cached is not None:
        return cached
    new_cop, new_blocked, new_quota = _pursuer_reply(board, waller, cop, thief, blocked, quota)
    outcome = False
    if new_cop is not None and mobility(board, thief, new_blocked) > 0:
        for action in legal_actions(board, thief, new_blocked):
            target = resolve_move(board, thief, action, new_blocked)
            if target == new_cop:
                continue  # stepping onto the pursuer is capture
            if action is not Action.STAY and mobility(board, target, new_blocked) == 0:
                continue  # moving into a fully sealed cell is capture (`AE-046`)
            if survives_walled(board, waller, new_cop, target,
                               steps_left - 1, new_blocked, new_quota, memo):
                outcome = True
                break
    memo[key] = outcome
    return outcome


def escape_actions_walled(
    board: Board, waller: WallerModel, thief: Coordinate, cop: Coordinate,
    steps_after: int, blocked: frozenset, quota: int, memo: WalledMemo,
) -> tuple[Action, ...]:
    """Return every legal action that still survives ``steps_after`` steps against ``waller``.

    Called at the Thief's decision point, where the pursuer has already acted this step — so
    ``cop``/``blocked``/``quota`` are the post-pursuer state the live Thief observes. The order
    of returned actions is the domain's fixed declaration order, so tie-breaks stay
    deterministic.
    """
    if steps_after < 0:
        raise ValueError(f"steps_after must be non-negative, got {steps_after}")
    winners = []
    for action in legal_actions(board, thief, blocked):
        target = resolve_move(board, thief, action, blocked)
        if target == cop:
            continue
        if action is not Action.STAY and mobility(board, target, blocked) == 0:
            continue
        if survives_walled(board, waller, cop, target, steps_after, blocked, quota, memo):
            winners.append(action)
    return tuple(winners)
