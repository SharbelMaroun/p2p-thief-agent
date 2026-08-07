"""The pursuer grid: shipped vs adaptive evasion against all three archetypes (`M6-030`).

The research report's threat 1 was "one Cop": the shipped numbers were earned against
the greedy harness pursuer, the stronger rows came from scratch code that no longer
exists, and the anticipating gap (8/24) had five failed fixes. This grid makes all of
it reproducible — the archetypes are committed (`strategy/pursuer_models.py`) and both
evasion arms play every perimeter opening against every archetype:

    uv run python scripts/experiment_pursuers.py    # writes results/pursuer_grid.json

The design is the report's own: 24 paired perimeter openings, deterministic
everything, league points as the binding metric (Appendix F pays 10 for the horizon,
5 for capture, nothing between). A robustness block re-runs the decisive matchup on a
larger board and a longer horizon, because the old policy's failure grew with the
horizon and a fix that only works at 35 would be a fix for the benchmark.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from p2p_thief_agent.domain.board import Board  # noqa: E402
from p2p_thief_agent.domain.movement import resolve_move  # noqa: E402
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief  # noqa: E402
from p2p_thief_agent.perception.field import blank_field, deposit, scent_likelihood  # noqa: E402
from p2p_thief_agent.strategy.adaptive_policy import (  # noqa: E402
    PursuerTracker,
    choose_adaptive_action,
)
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action  # noqa: E402
from p2p_thief_agent.strategy.pursuer_models import PURSUERS  # noqa: E402
from scripts.run_experiments import SCORE_CAPTURED, SCORE_SURVIVED, openings  # noqa: E402

RESULTS = ROOT / "results"
NO_BARRIERS = frozenset()


def _belief_from(scent, board: Board):
    observed = {(r, c): scent[r][c] for r in range(board.size)
                for c in range(board.size) if scent[r][c] > 0}
    belief = uniform_belief(board.size, board.size)
    if observed:
        belief = apply_evidence(belief, scent_likelihood(observed, board))
    return belief


def play(board: Board, cop, thief, pursuer, policy, steps: int) -> int:
    """One sub-game under the harness order; returns survival steps (== steps escapes)."""
    scent = blank_field(board)
    for step in range(1, steps + 1):
        cop = pursuer(board, cop, thief, NO_BARRIERS)
        scent = deposit(scent, board, cop)
        if cop == thief:
            return step - 1
        action = policy(board, thief, _belief_from(scent, board), step)
        thief = resolve_move(board, thief, action, NO_BARRIERS)
        if cop == thief:
            return step
    return steps


def shipped_arm(_board, _horizon, _memos):
    def policy(board, thief, belief, _step):
        return choose_evasive_action(board, thief, belief)
    return policy


def adaptive_arm(_board, horizon, memos):
    tracker = PursuerTracker(horizon, memos=memos)

    def policy(board, thief, belief, step):
        return choose_adaptive_action(board, thief, belief, tracker, step)
    return policy


ARMS = {"shipped": shipped_arm, "adaptive": adaptive_arm}


def grid_cell(size: int, steps: int, arm: str, pursuer_name: str) -> dict:
    board = Board(size=size)
    memos = {name: {} for name in PURSUERS}  # shared solver table for one config
    runs = []
    for cop, thief in openings(size):
        policy = ARMS[arm](board, steps, memos)
        runs.append(play(board, cop, thief, PURSUERS[pursuer_name], policy, steps))
    escapes = sum(1 for value in runs if value >= steps)
    points = sum(SCORE_SURVIVED if value >= steps else SCORE_CAPTURED for value in runs)
    return {"scenarios": len(runs), "escapes": escapes, "league_points": points,
            "total_steps": sum(runs)}


def truth_fed_cell(pursuer_name: str, size: int = 7, steps: int = 35) -> dict:
    """The diagnostic that localised the gap: the adaptive planner fed the true cell.

    Not a legal agent — an instrument, like the oracle arms both repositories use.
    24/24 here against every archetype is what proves the planner correct and the
    estimator to be the whole remaining gap.
    """
    from p2p_thief_agent.strategy.belief_policy import initial_belief  # noqa: PLC0415

    board = Board(size=size)
    memos = {name: {} for name in PURSUERS}
    escapes = 0
    for cop, thief in openings(size):
        tracker = PursuerTracker(steps, memos=memos)
        survived = steps
        for step in range(1, steps + 1):
            cop = PURSUERS[pursuer_name](board, cop, thief, NO_BARRIERS)
            if cop == thief:
                survived = step - 1
                break
            action = choose_adaptive_action(
                board, thief, initial_belief(board, cop), tracker, step)
            thief = resolve_move(board, thief, action, NO_BARRIERS)
            if thief == cop:
                survived = step
                break
        escapes += survived >= steps
    return {"scenarios": len(openings(size)), "escapes": escapes}


def pursuer_grid() -> dict:
    base = {arm: {name: grid_cell(7, 35, arm, name) for name in PURSUERS}
            for arm in ARMS}
    robustness = {
        "anticipating_9x9_h35": {arm: grid_cell(9, 35, arm, "anticipating") for arm in ARMS},
        "anticipating_7x7_h50": {arm: grid_cell(7, 50, arm, "anticipating") for arm in ARMS},
    }
    truth = {name: truth_fed_cell(name) for name in PURSUERS}
    return {"board": 7, "horizon": 35, "arms": base, "robustness": robustness,
            "truth_fed_adaptive": truth}


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    payload = pursuer_grid()
    (RESULTS / "pursuer_grid.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")
    for arm, row in payload["arms"].items():
        cells = "  ".join(f"{name}: {cell['escapes']}/{cell['scenarios']} ({cell['league_points']})"
                          for name, cell in row.items())
        print(f"{arm:9s} {cells}")
    for label, row in payload["robustness"].items():
        cells = "  ".join(f"{arm}: {cell['escapes']}/{cell['scenarios']}"
                          for arm, cell in row.items())
        print(f"{label:22s} {cells}")
    truth = "  ".join(f"{name}: {cell['escapes']}/{cell['scenarios']}"
                      for name, cell in payload["truth_fed_adaptive"].items())
    print(f"{'truth-fed adaptive':22s} {truth}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
