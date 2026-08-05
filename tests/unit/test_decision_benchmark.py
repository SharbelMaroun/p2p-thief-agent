"""`M6-011`: the per-turn decision cost stays well inside the response timeout.

One turn's decision is the belief update (scent + hint) plus the policy. It is pure Python
over the grid with no I/O, so it is bounded by construction; this measures it and asserts a
worst case orders of magnitude inside the 30 s response budget, so computational fairness is
never in doubt. Bounds are deliberately loose — the decision is sub-millisecond, so a slow
CI machine cannot flake them. Reproduce the recorded figures with
`scripts/benchmark_decision.py`, which writes `results/decision_benchmark.json`.
"""

import time

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.consume import consume_hint
from p2p_thief_agent.perception.field import scent_likelihood
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action

# network_and_league.response_timeout_sec = 30 s, from the signed match object `[AF-t19]`.
RESPONSE_TIMEOUT_MS = 30_000
SMELL = {(0, 0): 0.9, (0, 1): 0.62}
HINT = "the cop is north west somewhere"


def one_decision(board: Board, here: Coordinate) -> None:
    belief = apply_evidence(uniform_belief(board.size, board.size), scent_likelihood(SMELL, board))
    belief = consume_hint(belief, HINT, 0.5, board.size, board.size)
    choose_evasive_action(board, here, belief)


def worst_case_ms(size: int, iterations: int) -> float:
    board = Board(size=size)
    here = Coordinate(size // 2, size // 2)
    worst = 0.0
    for _ in range(iterations):
        start = time.perf_counter()
        one_decision(board, here)
        worst = max(worst, time.perf_counter() - start)
    return worst * 1000.0


def test_a_turn_at_the_negotiated_grid_is_orders_inside_the_timeout() -> None:
    """`M6-011a`: worst case at the 7×7 grid is a tiny fraction of the 30 s budget."""
    assert worst_case_ms(7, 500) < RESPONSE_TIMEOUT_MS / 100  # < 300 ms, huge headroom


def test_the_decision_scales_gently_above_the_minimum_grid() -> None:
    """Even well above the minimum grid, a decision stays far inside the budget."""
    assert worst_case_ms(20, 200) < RESPONSE_TIMEOUT_MS / 30
