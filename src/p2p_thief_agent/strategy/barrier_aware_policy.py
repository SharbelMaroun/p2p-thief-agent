"""Danger-gated barrier-aware evasion — the shipped policy stays default and fallback (`M6-035`).

The shipped `choose_adaptive_action` is already perfect against every *mover* archetype
(24/24 on the pursuer grid) and must not regress. Its one measured gap is a *walling*
opponent: it plans with `escape_search`, which freezes the barrier field, so it converts only
8/24 against the interceptor waller — yet the exact walled solver shows all 24 of those
openings are escapable with perfect play (`strategy/barrier_search.py`). This policy spends the
extra search only where a wall can actually hurt, and never at the cost of the mover-strong
behaviour.

What makes it safe to graft on is that **it only overrides an *unsafe* adaptive pick**: it keeps
the adaptive action whenever that action already survives the assumed waller, substitutes a
walled-safe action only when the adaptive pick would walk into the trap, and falls back to the
adaptive pick when the solver finds no guaranteed escape. So the shipped policy is both the
default and the floor, and the measured mover result is preserved — with the planner engaged on
every decision the four mover archetypes stay 24/24, identical to the adaptive policy.

**Engaged every step, not gated.** A first design only planned once a wall was disclosed or a
seal was one move away; measured, it recovered nothing (8/24 unchanged), because against a
walling interceptor the escape space is lost *before* a wall is ever placed — the gate opened
too late. Planning from the first move instead converts the interception waller 8/24 -> 24/24
even on the decoded belief, at every search depth from 6 up. The bounded depth (`DEFAULT_DEPTH_CAP`)
keeps the worst decision well inside the response budget; the legacy `is_dangerous` gate is
retained only for the measured comparison (`always=False`).

Deterministic and history-free (book §6 sanctions deterministic look-ahead search): identical
inputs give an identical action, so replay verifies the logged move and the audit stays free.
The default production strategy remains ``"current"``; this is opt-in behind a private selector.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.adaptive_policy import PursuerTracker, choose_adaptive_action
from p2p_thief_agent.strategy.barrier_search import WallerModel, escape_actions_walled
from p2p_thief_agent.strategy.baseline import _ACTION_ORDER, is_dead_end, mobility
from p2p_thief_agent.strategy.belief_policy import Grid, believed_cop_cell
from p2p_thief_agent.strategy.metrics import manhattan_distance, wall_pressure
from p2p_thief_agent.strategy.waller_models import greedy_waller, interceptor_waller

# Hardest plausible waller first: an action safe against the interception waller is the
# strongest guarantee, and the greedy waller is the cheaper shape to fall back to.
DEFAULT_WALLERS: tuple[WallerModel, ...] = (interceptor_waller, greedy_waller)
# Receding horizon. Conversion is already 24/24 against both wallers at depth 6; 8 is a small
# margin over that floor, and keeps the worst decision far inside the 30 s response budget.
DEFAULT_DEPTH_CAP = 8
DEFAULT_PRESSURE_GATE = 1  # legacy gate only (always=False): wall_pressure <= this is danger


def is_dangerous(
    board: Board, position: Coordinate, believed_cop: Coordinate,
    barriers: frozenset[Coordinate], pressure_gate: int = DEFAULT_PRESSURE_GATE,
) -> bool:
    """Whether a wall could plausibly matter now — the only time the planner is worth its cost.

    Opens on either legally-known signal: the Police has *disclosed* a barrier (it is a
    waller, proven, not guessed), or the believed Police is within one wall of sealing us
    (`wall_pressure`), which is where a first wall turns fatal. A pure mover triggers neither.
    """
    if barriers:
        return True
    return wall_pressure(board, position, believed_cop, barriers) <= pressure_gate


def _rank_within(
    board: Board, position: Coordinate, believed_cop: Coordinate,
    blocked: frozenset[Coordinate], actions: Sequence[Action],
) -> Action:
    """Pick among already-safe actions by the shipped criteria (deterministic tie-break).

    Reuses exactly the measures the shipped policy trusts — avoid the single-wall trap, avoid
    dead ends, then maximise distance-plus-room — so the substitute stays a good move, not
    merely a safe one.
    """
    targets = {action: resolve_move(board, position, action, blocked) for action in actions}

    def rank(action: Action) -> tuple:
        target = targets[action]
        pressure = wall_pressure(board, target, believed_cop, blocked)
        return (pressure == 0, pressure == 1,
                is_dead_end(board, target, position, blocked),
                -(manhattan_distance(target, believed_cop) + mobility(board, target, blocked)),
                _ACTION_ORDER.index(action))

    return min(actions, key=rank)


def choose_barrier_aware_action(
    board: Board,
    position: Coordinate,
    belief: Grid,
    tracker: PursuerTracker,
    step: int,
    barriers: Iterable[Coordinate] = (),
    *,
    quota_remaining: int,
    threshold: int = 35,
    wallers: Sequence[WallerModel] = DEFAULT_WALLERS,
    depth_cap: int = DEFAULT_DEPTH_CAP,
    always: bool = True,
    pressure_gate: int = DEFAULT_PRESSURE_GATE,
    stats: dict | None = None,
) -> Action:
    """Return the shipped action, or a walled-safe substitute when a wall would trap it.

    ``always`` (the default) plans on every decision — the configuration measured to convert
    the walling weakness. ``always=False`` restores the legacy `is_dangerous` gate, kept only
    for the measured comparison that showed gating recovers nothing.
    """
    blocked = frozenset(barriers)
    adaptive = choose_adaptive_action(board, position, belief, tracker, step, blocked)
    believed = believed_cop_cell(belief, board)
    if stats is not None:
        stats["decisions"] = stats.get("decisions", 0) + 1
    if not always and not is_dangerous(board, position, believed, blocked, pressure_gate):
        return adaptive
    if stats is not None:
        stats["activations"] = stats.get("activations", 0) + 1
    remaining = max(threshold - step, 0)
    depth = min(remaining, depth_cap)
    legal = set(legal_actions(board, position, blocked))
    for waller in wallers:
        memo: dict = {}
        safe = [a for a in escape_actions_walled(
            board, waller, position, believed, depth, blocked, max(quota_remaining, 0), memo)
            if a in legal]
        if stats is not None:
            stats["nodes"] = stats.get("nodes", 0) + len(memo)
        if safe:
            if adaptive in safe:
                return adaptive
            if stats is not None:
                stats["overrides"] = stats.get("overrides", 0) + 1
            return _rank_within(board, position, believed, blocked, safe)
    if stats is not None:
        stats["fallbacks"] = stats.get("fallbacks", 0) + 1
    return adaptive


def evasion_action(
    strategy: str, board: Board, position: Coordinate, belief: Grid,
    tracker: PursuerTracker, step: int, blocked: frozenset[Coordinate],
    *, threshold: int, quota_remaining: int,
) -> Action:
    """Dispatch the live evasion by named strategy — the one seam the turn loop calls.

    ``"current"`` (the production default) is the shipped `choose_adaptive_action`, byte for
    byte; ``"barrier_aware_v2"`` is the always-on walled planner. An unknown name resolves to
    ``"current"`` so a stray config value can never leave the Thief without a legal move.
    """
    if strategy == "barrier_aware_v2":
        return choose_barrier_aware_action(
            board, position, belief, tracker, step, blocked,
            quota_remaining=quota_remaining, threshold=threshold)
    return choose_adaptive_action(board, position, belief, tracker, step, blocked)
