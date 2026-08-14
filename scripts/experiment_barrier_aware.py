"""The barrier-aware grid: the walled planner vs the shipped policy, paired (`M6-035`).

Answers the one question the experimental strategy exists to answer, on the same 24 perimeter
openings and league-point metric the other grids use: does planning against the walling
opponent every step convert the waller weakness, and does it cost anything against the movers
it must not regress? Both arms are belief-fed (the decoded, model-matched estimate the live
Thief carries) and barrier-aware (they receive the disclosed barriers, as the live turn does),
so the only difference measured is the planner itself.

    uv run python scripts/experiment_barrier_aware.py    # writes results/barrier_aware_grid.json

Latency is recorded across every decision the new arm makes (median/p95/p99/max) so the report
can show the worst turn stays far inside the 30 s response budget. Deterministic throughout.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from p2p_thief_agent.domain.board import Board  # noqa: E402
from p2p_thief_agent.domain.movement import resolve_move  # noqa: E402
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief  # noqa: E402
from p2p_thief_agent.perception.emitter_decoder import emitter_likelihood  # noqa: E402
from p2p_thief_agent.perception.field import blank_field, deposit  # noqa: E402
from p2p_thief_agent.strategy.adaptive_policy import (  # noqa: E402
    PursuerTracker,
    choose_adaptive_action,
)
from p2p_thief_agent.strategy.barrier_aware_policy import choose_barrier_aware_action  # noqa: E402
from p2p_thief_agent.strategy.pursuer_models import PURSUERS  # noqa: E402
from p2p_thief_agent.strategy.waller_models import WALLERS  # noqa: E402
from scripts.run_experiments import SCORE_CAPTURED, SCORE_SURVIVED, openings  # noqa: E402

RESULTS = ROOT / "results"
WALL_QUOTA = 14
DEPTH = 8
LATENCY_MS: list[float] = []


def _decoded(board: Board, observed: dict, state: dict):
    if not observed:
        return uniform_belief(board.size, board.size)
    likelihood = emitter_likelihood(board, observed, state.get("previous"))
    state["previous"] = observed
    return apply_evidence(uniform_belief(board.size, board.size), likelihood)


def _decide(arm: str, board, thief, belief, step, blocked, quota, tracker):
    start = time.perf_counter()
    if arm == "adaptive":
        action = choose_adaptive_action(board, thief, belief, tracker, step, blocked)
    else:
        action = choose_barrier_aware_action(board, thief, belief, tracker, step, blocked,
                                             quota_remaining=quota, threshold=35, depth_cap=DEPTH)
    if arm == "barrier_aware":
        LATENCY_MS.append((time.perf_counter() - start) * 1000)
    return action


def _play_waller(board, cop, thief, waller, arm, steps):
    from p2p_thief_agent.strategy.metrics import mobility  # noqa: PLC0415

    scent = blank_field(board)
    blocked, quota = frozenset(), WALL_QUOTA
    tracker, bstate = PursuerTracker(steps), {}
    for step in range(1, steps + 1):
        new_cop, wall = waller(board, cop, thief, blocked, quota)
        if wall is not None:
            blocked, quota = blocked | {wall}, quota - 1
            if wall == thief:
                return step - 1
        else:
            cop = new_cop
        scent = deposit(scent, board, cop)
        if cop == thief or mobility(board, thief, blocked) == 0:
            return step - 1
        observed = {(r, c): scent[r][c] for r in range(board.size)
                    for c in range(board.size) if scent[r][c] > 0}
        belief = _decoded(board, observed, bstate)
        thief = resolve_move(board, thief, _decide(arm, board, thief, belief, step, blocked, quota, tracker), blocked)
        if cop == thief or mobility(board, thief, blocked) == 0:
            return step
    return steps


def _play_mover(board, cop, thief, mover, arm, steps):
    scent = blank_field(board)
    tracker, bstate = PursuerTracker(steps), {}
    for step in range(1, steps + 1):
        cop = mover(board, cop, thief, frozenset())
        scent = deposit(scent, board, cop)
        if cop == thief:
            return step - 1
        observed = {(r, c): scent[r][c] for r in range(board.size)
                    for c in range(board.size) if scent[r][c] > 0}
        belief = _decoded(board, observed, bstate)
        thief = resolve_move(board, thief, _decide(arm, board, thief, belief, step, frozenset(), WALL_QUOTA, tracker), frozenset())
        if cop == thief:
            return step
    return steps


def _cell(play, table, name, arm, size=7, steps=35):
    board = Board(size=size)
    runs = [play(board, cop, thief, table[name], arm, steps) for cop, thief in openings(size)]
    escapes = sum(1 for v in runs if v >= steps)
    points = sum(SCORE_SURVIVED if v >= steps else SCORE_CAPTURED for v in runs)
    return {"escapes": escapes, "scenarios": len(runs), "league_points": points,
            "worst_survival": min(runs), "median_survival": statistics.median(runs)}


def grid() -> dict:
    wallers = {name: {arm: _cell(_play_waller, WALLERS, name, arm) for arm in ("adaptive", "barrier_aware")}
               for name in WALLERS}
    movers = {name: {arm: _cell(_play_mover, PURSUERS, name, arm) for arm in ("adaptive", "barrier_aware")}
              for name in PURSUERS}
    LATENCY_MS.sort()
    n = len(LATENCY_MS)
    latency = {"decisions": n, "median_ms": round(statistics.median(LATENCY_MS), 2),
               "p95_ms": round(LATENCY_MS[int(0.95 * n)], 2),
               "p99_ms": round(LATENCY_MS[int(0.99 * n)], 2), "max_ms": round(max(LATENCY_MS), 2),
               "budget_ms": 30000}
    return {"board": 7, "horizon": 35, "depth_cap": DEPTH, "wall_quota": WALL_QUOTA,
            "wallers": wallers, "movers": movers, "latency": latency}


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    payload = grid()
    (RESULTS / "barrier_aware_grid.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")
    for family, rows in (("waller", payload["wallers"]), ("mover", payload["movers"])):
        for name, arms in rows.items():
            a, b = arms["adaptive"], arms["barrier_aware"]
            print(f"{family:7s} {name:20s} adaptive {a['escapes']:2d}/{a['scenarios']} "
                  f"-> barrier_aware {b['escapes']:2d}/{b['scenarios']}")
    print(f"latency: {payload['latency']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
