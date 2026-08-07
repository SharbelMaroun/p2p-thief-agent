"""Parameter research: real sweeps through the real evasion harness (`M9-006`, `M9-007`).

Guidelines §9.1 asks for "systematic experiments with controlled changes to parameters";
`M9-006c` for "experiment tables with **run counts**, not anecdotes"; the book for research
"based on numbers and not on guesses" (p.142/266).

Every figure comes from `tests.unit.test_strategy_comparison.simulate` — the same harness
the `M6-015` test gates — so the numbers reported here are the numbers that suite asserts.

    uv run python scripts/run_experiments.py

**The scenario set is widened, not repeated.** The shipped comparison uses four fixed
openings, which is four data points. The harness is fully deterministic, so running it
forty times would return the identical answer forty times and inflate `n` without adding a
single bit of evidence — the one way a run count can lie. Instead this enumerates every
opening on the board's perimeter, which is a genuinely larger sample of the same question.

**Which parameters may move.** Appendix F marks each row Fixed, Minimum or Negotiation:
Minimum "may be raised by agreement but never lowered". Board size (7), step limit (35) and
survival threshold (35) are Minimum, so the sweeps run **upward from** them; sweeping below
would study a configuration rule 12 forbids.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from p2p_thief_agent.analysis import paired_compare, summarise  # noqa: E402
from p2p_thief_agent.domain.board import Board  # noqa: E402
from p2p_thief_agent.domain.coordinates import Coordinate  # noqa: E402
from tests.unit.test_strategy_comparison import _belief, _blind, simulate  # noqa: E402

RESULTS = ROOT / "results"
ARMS = {"blind": _blind, "belief": _belief}
MINIMA = {"board_size": 7, "max_steps": 35}
# Appendix F, both Fixed: the Thief scores 10 for surviving the threshold and 5 for being
# captured. Partial survival earns nothing extra -- which is the whole reason this file
# reports league points as well as steps. See `league_points`.
SCORE_SURVIVED, SCORE_CAPTURED = 10, 5


def perimeter(size: int) -> list[Coordinate]:
    """Every cell on the board's edge, in a stable order."""
    edge = sorted({(r, c) for r in range(size) for c in range(size)
                   if r in (0, size - 1) or c in (0, size - 1)})
    return [Coordinate(r, c) for r, c in edge]


def openings(size: int) -> list[tuple[Coordinate, Coordinate]]:
    """Cop and Thief on opposite perimeter cells — a systematically widened scenario set.

    Opposite rather than arbitrary, so no scenario starts already captured or already
    adjacent, which would measure the opening rather than the policy.
    """
    cells = perimeter(size)
    half = len(cells) // 2
    return [(cells[i], cells[(i + half) % len(cells)]) for i in range(len(cells))]


def play(size: int, steps: int, arm: str) -> list[float]:
    """Survival steps for one arm across every opening on a `size` board."""
    board = Board(size=size)
    return [float(simulate(board, cop, thief, ARMS[arm], steps))
            for cop, thief in openings(size)]


def league_points(runs: list[float], steps: int) -> int:
    """What the scoring table actually pays for these runs.

    **This exists because steps and points disagree.** `M6-015` asserts belief-driven
    evasion beats the blind baseline on *total survival steps*, and it does. But Appendix F
    pays 10 for reaching the threshold and 5 for being captured, with nothing in between —
    so a policy that reliably survives 28 of 35 turns scores exactly as badly as one caught
    on turn 2. Reporting steps alone would recommend a strategy the rules do not reward.
    """
    return sum(SCORE_SURVIVED if value >= steps else SCORE_CAPTURED for value in runs)


def arms_comparison(size: int = 7, steps: int = 35) -> dict:
    """`M9-007a`: blind baseline against belief-driven evasion, paired per scenario."""
    played = {arm: play(size, steps, arm) for arm in ARMS}
    report = {arm: summarise(values).as_dict() for arm, values in played.items()}
    report["paired_belief_vs_blind"] = paired_compare(played["belief"],
                                                      played["blind"]).as_dict()
    report["scenarios"] = len(played["blind"])
    report["board_size"] = size
    report["max_steps"] = steps
    report["survived_full_horizon"] = {
        arm: sum(1 for v in values if v >= steps) for arm, values in played.items()}
    report["total_steps"] = {arm: sum(values) for arm, values in played.items()}
    report["league_points"] = {arm: league_points(values, steps)
                               for arm, values in played.items()}
    report["metric_disagreement"] = (
        report["total_steps"]["belief"] > report["total_steps"]["blind"]
        and report["league_points"]["belief"] < report["league_points"]["blind"])
    return report


def sweep_board_size(sizes=(7, 8, 9, 10, 11, 12), steps: int = 35) -> dict:
    """A bigger board gives the Thief more room. Does it convert to survival?"""
    points = []
    for size in sizes:
        blind, belief = play(size, steps, "blind"), play(size, steps, "belief")
        points.append({"value": size, "scenarios": len(belief),
                       "blind": summarise(blind).as_dict(),
                       "belief": summarise(belief).as_dict(),
                       "paired": paired_compare(belief, blind).as_dict()})
    return {"parameter": "board_and_agents.grid_size", "appendix_f_status": "Minimum",
            "minimum": MINIMA["board_size"], "max_steps": steps, "points": points}


def sweep_horizon(limits=(35, 45, 55, 65, 75), size: int = 7) -> dict:
    """A longer game is more time to be caught. Where does survival stop being reachable?"""
    points = []
    for steps in limits:
        blind, belief = play(size, steps, "blind"), play(size, steps, "belief")
        points.append({
            "value": steps, "scenarios": len(belief),
            "blind": summarise(blind).as_dict(), "belief": summarise(belief).as_dict(),
            "belief_survived_full": sum(1 for v in belief if v >= steps),
            "blind_survived_full": sum(1 for v in blind if v >= steps),
            "league_points": {"blind": league_points(blind, steps),
                              "belief": league_points(belief, steps)},
        })
    return {"parameter": "movement_and_barriers.survival_threshold",
            "appendix_f_status": "Minimum", "minimum": MINIMA["max_steps"],
            "board_size": size, "points": points}


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    produced = {
        "strategy_arms.json": arms_comparison(),
        "sweep_board_size.json": sweep_board_size(),
        "sweep_horizon.json": sweep_horizon(),
    }
    for name, payload in produced.items():
        (RESULTS / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                                    "utf-8")
        print(f"results/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
