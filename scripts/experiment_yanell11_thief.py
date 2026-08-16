"""Can our Thief survive yanell11's Cop? (2026-08-16)

Run 4 lost all three Thief sub-games to a capture at step 30, and the three logs are
*identical* — same cells, same moves, same ending. That is one reproducible failure, not
three, and reading it back gives the shape:

    19..23  [0,5] -> [1,5] -> [0,5] -> [1,5] -> [0,5]   oscillating, net zero displacement
    26,27   STAY at distance 2, then STAY at distance 1
    28      W to [0,4], the Cop follows to [0,5]
    29,30   STAY, STAY at distance 1                     -> captured

Two separate mistakes. It **pins itself to row 0**, an edge where north is not an escape
and the reachable set is half a disc; and it **plays STAY while the pursuer is adjacent**,
which is a chosen capture rather than a forced one.

Arms are the live decision path (`make_decide`), fed the Cop's emissions through the same
`smell_grid` shape the wire carries. Opponents:

* ``run4-gNN`` -- their Cop's recorded trajectory, move for move. Fixed, so it answers:
  does this arm survive the exact attack that beat us?
* ``chaser``   -- greedy minimum-distance pursuit, reacting to where we actually are.
* ``cutoff``   -- pursues the cell that minimises our *escape room* rather than our
  distance, which is what a competent Cop does and what a pure chaser never does.

Usage:  uv run python scripts/experiment_yanell11_thief.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p2p_thief_agent.domain.board import Board  # noqa: E402
from p2p_thief_agent.domain.coordinates import Coordinate  # noqa: E402
from p2p_thief_agent.orchestration.thief_policy import make_decide  # noqa: E402
from p2p_thief_agent.perception.field import blank_field, deposit  # noqa: E402
from p2p_thief_agent.perception.observation import encode_smell_grid  # noqa: E402

GRID = 7
HORIZON = 35
THIEF_START = (3, 3)
COP_START = (0, 0)
REPO = Path(__file__).resolve().parents[1]

REPLAYS = {
    "run4-g02": "games/friendly-yanell11-run4/opponent_audit_sharNamr-vs-yanell11_g02.json",
    "run4-g04": "games/friendly-yanell11-run4/opponent_audit_sharNamr-vs-yanell11_g04.json",
    "run4-g06": "games/friendly-yanell11-run4/opponent_audit_sharNamr-vs-yanell11_g06.json",
}


def recorded_cop(which: str) -> list[Coordinate]:
    data = json.loads((REPO / REPLAYS[which]).read_text(encoding="utf-8"))
    rows = [r["payload"] for a in data["audits"] for r in a.get("records", [])]
    cells = []
    for row in sorted(rows, key=lambda r: r.get("step") or 0):
        pos = row.get("position")
        if isinstance(pos, list) and len(pos) == 2:
            cells.append(Coordinate(pos[0], pos[1]))
    return cells


def neighbours(board: Board, cell: Coordinate) -> list[Coordinate]:
    out = [cell]
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nxt = Coordinate(cell.row + dr, cell.col + dc)
        if board.contains(nxt):
            out.append(nxt)
    return out


def escape_room(board: Board, thief: Coordinate, cop: Coordinate) -> int:
    """How many cells the Thief can still reach before the Cop cuts them off.

    A crude Voronoi count: cells strictly closer to the Thief than to the Cop. This is the
    quantity a cornered Thief has driven to almost nothing, and the quantity a competent
    Cop attacks -- distance alone does not capture it.
    """
    room = 0
    for r in range(GRID):
        for c in range(GRID):
            dt = abs(r - thief.row) + abs(c - thief.col)
            dc_ = abs(r - cop.row) + abs(c - cop.col)
            room += dt < dc_
    return room


def approach(n: Coordinate, thief: Coordinate) -> tuple[int, int]:
    """Manhattan distance, then SQUARED distance as the tie-break.

    The squared term is load-bearing, not decoration. Manhattan ties constantly on a grid
    -- from [0,5] chasing [5,4], both [1,5] and [0,4] score 5 -- and breaking those ties by
    (row, col) pins the pursuer to the top edge, where it oscillates on row 0 forever and
    never closes. That bug made every Thief arm look invincible in this harness. Squared
    distance prefers the move that shortens the LONGER axis, which is what closing in
    actually means: [1,5] scores 17 against [0,4]'s 25.
    """
    dr, dc = abs(n.row - thief.row), abs(n.col - thief.col)
    return dr + dc, dr * dr + dc * dc


def move_cop(kind: str, board: Board, cop: Coordinate, thief: Coordinate) -> Coordinate:
    if kind == "chaser":
        return min(neighbours(board, cop), key=lambda n: approach(n, thief))
    # cutoff: shrink the Thief's reachable region, tie-broken by closing distance
    return min(neighbours(board, cop),
               key=lambda n: (escape_room(board, thief, n), *approach(n, thief)))


def play(strategy: str, opponent: str, *, use_cop_start: bool) -> tuple[bool, int, int]:
    """Return (survived, steps, min_distance_reached)."""
    board = Board(size=GRID)
    decide = make_decide(
        grid_size=GRID, start=THIEF_START, threshold=HORIZON, strategy=strategy,
        cop_start=COP_START if use_cop_start else None,
    )
    path = recorded_cop(opponent) if opponent in REPLAYS else []
    cop = Coordinate(*COP_START)
    trail = blank_field(board)
    closest = 99

    thief = Coordinate(*THIEF_START)
    for step in range(1, HORIZON + 1):
        # THE COP MOVES FIRST. In sub-games 2/4/6 the Cop initiates the turn exchange --
        # it sends `receive_turn`, we answer -- so within one step it acts while we are
        # still on our current cell. That ordering is why run 4's losses were legitimate:
        # they landed on the cell we were standing on, and our honest `answer_claim`
        # conceded from the pre-move cell. Modelling the Thief as moving first (which this
        # harness did at first) makes every arm survive everything, because the Cop can
        # then only ever land on a cell we have already left.
        #
        # The practical consequence for strategy: ending a turn at distance 1 is LOSING,
        # not merely dangerous -- the Cop simply steps onto us before we move again.
        cop = path[step] if (path and step < len(path)) else move_cop(
            opponent if opponent in ("chaser", "cutoff") else "chaser", board, cop, thief)
        if cop == thief:
            return False, step, 0

        trail = deposit(trail, board, cop)
        # `encode_smell_grid` takes a {(row, col): intensity} mapping, not the grid tuple.
        observed = {(r, c): trail[r][c]
                    for r in range(GRID) for c in range(GRID) if trail[r][c] > 0}
        incoming = {"smell_grid": encode_smell_grid(observed), "step": step}
        # The Thief returns (wire message, sealed record) -- the reverse of the Cop's
        # order. The true cell is in the SEALED payload; the wire message carries only
        # the commit and the emission, which is the whole point of commit-reveal.
        _message, sealed = decide(incoming, step)
        thief = Coordinate(*sealed["payload"]["position"])
        if thief == cop:
            return False, step, 0
        closest = min(closest, abs(thief.row - cop.row) + abs(thief.col - cop.col))
    return True, HORIZON, closest


ARMS = [("current", True), ("barrier_aware_v2", True), ("open_field_v3", True)]
OPPONENTS = [*REPLAYS, "chaser", "cutoff"]

print(f"{'thief arm':<28}" + "".join(f"{o:>12}" for o in OPPONENTS))
print("-" * (28 + 12 * len(OPPONENTS)))
for strategy, cop_start in ARMS:
    label = f"{strategy}{'+copstart' if cop_start else ''}"
    cells, lived = [], 0
    for opponent in OPPONENTS:
        try:
            survived, steps, _closest = play(strategy, opponent, use_cop_start=cop_start)
            lived += survived
            cells.append(f"{'SURVIVE' if survived else 'caught@' + str(steps):>12}")
        except Exception as exc:  # noqa: BLE001 - report, do not abort the sweep
            cells.append(f"{type(exc).__name__[:11]:>12}")
    print(f"{label:<28}" + "".join(cells) + f"   survived {lived}/{len(OPPONENTS)}")
