"""`M6-019`: the deterministic baseline must beat random legal movement.

Before belief is added, the movement policy has to earn its keep against chance: a Thief
that shuffles at random should die sooner than one that keeps its mobility and shuns dead
ends. The pursuit harness and scenarios are shared with `M6-015`; the control here is a
seeded random walk over legal moves, averaged across fixed seeds for a stable comparison
(`M6-019a`). Survival totals are recorded for `M9-007a` (`M6-019b`).
"""

import random
from statistics import mean

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.movement import legal_actions
from p2p_thief_agent.strategy.baseline import choose_action
from tests.unit.test_strategy_comparison import SCENARIOS, simulate

BOARD = Board(size=7)
NO_BARRIERS = frozenset()
SEEDS = range(5)


def _baseline_policy(board: Board, thief, _smell):
    return choose_action(board, thief, (), NO_BARRIERS)


def _random_policy(seed: int):
    rng = random.Random(seed)

    def policy(board: Board, thief, _smell):
        return rng.choice(legal_actions(board, thief, NO_BARRIERS))

    return policy


def _total_survival(policy) -> int:
    return sum(simulate(BOARD, cop, thief, policy, 35) for cop, thief in SCENARIOS)


def test_the_baseline_beats_random_legal_movement() -> None:
    baseline = _total_survival(_baseline_policy)
    random_mean = mean(_total_survival(_random_policy(seed)) for seed in SEEDS)
    assert baseline > random_mean
