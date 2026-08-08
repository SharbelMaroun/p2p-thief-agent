"""The waller grid: evasion against Police that spend turns on walls (`M6-032`).

Every pursuer the grid has measured so far only moves — yet the book gives the Police
a wall quota (Appendix F minimum 14), walling the thief's cell captures, and a thief
whose every exit is sealed is captured (`AE-046`). A league opponent that converts its
quota into traps is therefore the strongest realistic threat, and no mover model can
express it. This grid measures survival against two walling instruments:

- **greedy_waller** — the reference chase with finishing walls: wall the thief's cell
  when in range, else seal its last exits when it runs low, else chase greedily.
- **interceptor_waller** — the same wall rules over the summed-distance interception
  chase: the strongest shape a strong classmate can cheaply ship.

The wallers are instruments and read true cells (`AE-8` binds agents, not
instruments). Wall candidates are the four cells orthogonally adjacent to the Police
(book §3.4 range, own-cell placement left out as an instrument simplification), in a
fixed deterministic order. Run:

    uv run python scripts/experiment_wallers.py    # writes results/waller_grid.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from p2p_thief_agent.domain.board import Board  # noqa: E402
from p2p_thief_agent.domain.coordinates import Coordinate  # noqa: E402
from p2p_thief_agent.domain.movement import resolve_move  # noqa: E402
from p2p_thief_agent.perception.field import blank_field, deposit  # noqa: E402
from p2p_thief_agent.strategy.metrics import mobility  # noqa: E402
from p2p_thief_agent.strategy.pursuer_models import (  # noqa: E402
    PURSUERS,
    greedy_step,
    interceptor_step,
)
from scripts.experiment_pursuers import ARMS  # noqa: E402
from scripts.run_experiments import SCORE_CAPTURED, SCORE_SURVIVED, openings  # noqa: E402

RESULTS = ROOT / "results"
WALL_QUOTA = 14


def _wall_candidates(board: Board, cop: Coordinate, blocked: frozenset) -> list[Coordinate]:
    """The four in-range wall cells in a fixed row-major order."""
    cells = [Coordinate(cop.row + dr, cop.col + dc)
             for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0))]
    return [cell for cell in cells
            if board.contains(cell) and cell not in blocked]


def _waller(mover):
    """Wrap a mover into a walling pursuer: finish, seal, else chase."""
    def pursue(board: Board, cop: Coordinate, thief: Coordinate,
               blocked: frozenset, quota: int):
        if quota > 0:
            candidates = _wall_candidates(board, cop, blocked)
            for cell in candidates:
                if cell == thief:
                    return cop, cell  # a wall on the thief's cell captures (§3.4)
            if mobility(board, thief, blocked) <= 2:
                for cell in candidates:
                    if mobility(board, thief, blocked | {cell}) < mobility(board, thief, blocked):
                        return cop, cell  # seal an exit while it is scarce
        return mover(board, cop, thief, blocked), None
    return pursue


WALLERS = {"greedy_waller": _waller(greedy_step),
           "interceptor_waller": _waller(interceptor_step)}


def play_walled(board: Board, cop, thief, waller, policy, steps: int) -> int:
    """One sub-game against a walling pursuer; returns survival steps."""
    scent = blank_field(board)
    blocked: frozenset[Coordinate] = frozenset()
    quota = WALL_QUOTA
    for step in range(1, steps + 1):
        cop, wall = waller(board, cop, thief, blocked, quota)
        if wall is not None:
            blocked, quota = blocked | {wall}, quota - 1
            if wall == thief:
                return step - 1
        scent = deposit(scent, board, cop)
        if cop == thief or mobility(board, thief, blocked) == 0:
            return step - 1
        observed = {(r, c): scent[r][c] for r in range(board.size)
                    for c in range(board.size) if scent[r][c] > 0}
        action = policy(board, thief, observed, step)
        thief = resolve_move(board, thief, action, blocked)
        if cop == thief:
            return step
        if mobility(board, thief, blocked) == 0:
            return step  # every exit sealed is a capture (`AE-046`)
    return steps


def grid_cell(size: int, steps: int, arm: str, waller_name: str) -> dict:
    board = Board(size=size)
    runs = []
    for cop, thief in openings(size):
        policy = ARMS[arm](board, steps, {name: {} for name in PURSUERS})
        runs.append(play_walled(board, cop, thief, WALLERS[waller_name], policy, steps))
    escapes = sum(1 for value in runs if value >= steps)
    points = sum(SCORE_SURVIVED if value >= steps else SCORE_CAPTURED for value in runs)
    return {"scenarios": len(runs), "escapes": escapes, "league_points": points,
            "total_steps": sum(runs)}


def waller_grid() -> dict:
    arms = ("shipped_decoded", "adaptive_decoded")
    base = {arm: {name: grid_cell(7, 35, arm, name) for name in WALLERS} for arm in arms}
    robustness = {"interceptor_waller_9x9_h35":
                  {arm: grid_cell(9, 35, arm, "interceptor_waller") for arm in arms}}
    return {"board": 7, "horizon": 35, "wall_quota": WALL_QUOTA,
            "arms": base, "robustness": robustness}


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    payload = waller_grid()
    (RESULTS / "waller_grid.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")
    for arm, row in payload["arms"].items():
        cells = "  ".join(f"{name}: {cell['escapes']}/{cell['scenarios']} ({cell['league_points']})"
                          for name, cell in row.items())
        print(f"{arm:16s} {cells}")
    for label, row in payload["robustness"].items():
        cells = "  ".join(f"{arm}: {cell['escapes']}/{cell['scenarios']}" for arm, cell in row.items())
        print(f"{label:28s} {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
