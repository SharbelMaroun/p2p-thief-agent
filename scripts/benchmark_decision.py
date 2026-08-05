"""Benchmark the per-turn decision cost and record it (`M6-011`).

Measures one turn's decision — the belief update from a scent observation and a hint, then
the evasive-move policy — across grid sizes, and writes the summary to
``results/decision_benchmark.json`` as reproducible research evidence for the
computational-fairness claim (`M9-006`). Run with ``uv run python scripts/benchmark_decision.py``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.consume import consume_hint
from p2p_thief_agent.perception.field import scent_likelihood
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action

RESPONSE_TIMEOUT_MS = 30_000  # network_and_league.response_timeout_sec = 30 s
SMELL = {(0, 0): 0.9, (0, 1): 0.62}
HINT = "the cop is north west somewhere"


def _measure(size: int, iterations: int) -> dict[str, float | str | int]:
    board = Board(size=size)
    here = Coordinate(size // 2, size // 2)
    total, worst = 0.0, 0.0
    for _ in range(iterations):
        start = time.perf_counter()
        belief = apply_evidence(uniform_belief(size, size), scent_likelihood(SMELL, board))
        belief = consume_hint(belief, HINT, 0.5, size, size)
        choose_evasive_action(board, here, belief)
        elapsed = time.perf_counter() - start
        total += elapsed
        worst = max(worst, elapsed)
    return {
        "grid": f"{size}x{size}",
        "iterations": iterations,
        "mean_ms": round(1000 * total / iterations, 4),
        "worst_ms": round(1000 * worst, 4),
        "budget_ms": RESPONSE_TIMEOUT_MS,
    }


def run() -> list[dict[str, float | str | int]]:
    """Measure at the negotiated grid and a larger one; write and return the summary."""
    rows = [_measure(7, 3000), _measure(20, 1000)]
    out = Path(__file__).resolve().parents[1] / "results" / "decision_benchmark.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


if __name__ == "__main__":
    for row in run():
        print(f"{row['grid']:>7}: mean {row['mean_ms']} ms, worst {row['worst_ms']} ms "
              f"(budget {row['budget_ms']} ms)")
