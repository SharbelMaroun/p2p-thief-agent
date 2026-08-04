"""`M6-015`: belief-driven evasion must beat the blind baseline — measured, or reverted.

A deterministic pursuing Cop (fixed policy, fixed start scenarios, `M6-015a`) chases the
Thief; the Cop deposits scent it cannot help emitting, and the Thief either ignores it
(blind baseline) or senses it and flees the believed Cop cell (belief-driven). Survival is
the steps the Thief lasts. If belief-driven ever failed to beat blind, the number would say
so and the policy would be reverted — a negative result is evidence, not something to hide
(`M6-015b`). `scripts/strategy_comparison.py` records the figures to `results/`.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.field import blank_field, deposit, scent_likelihood
from p2p_thief_agent.strategy.baseline import choose_action
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action
from p2p_thief_agent.strategy.metrics import manhattan_distance

NO_BARRIERS = frozenset()
SCENARIOS = [
    (Coordinate(0, 0), Coordinate(6, 6)),
    (Coordinate(6, 0), Coordinate(0, 6)),
    (Coordinate(0, 6), Coordinate(6, 0)),
    (Coordinate(3, 0), Coordinate(3, 6)),
]


def _cop_pursues(board: Board, cop: Coordinate, thief: Coordinate) -> Coordinate:
    """Deterministic greedy pursuit: the legal move that minimises distance to the thief."""
    targets = {a: resolve_move(board, cop, a, NO_BARRIERS) for a in legal_actions(board, cop, NO_BARRIERS)}
    return targets[min(targets, key=lambda a: (manhattan_distance(targets[a], thief), a.value))]


def _observed(scent, board: Board) -> dict:
    return {(r, c): scent[r][c] for r in range(board.size) for c in range(board.size) if scent[r][c] > 0}


def _blind(board: Board, thief: Coordinate, _smell: dict):
    return choose_action(board, thief, (), NO_BARRIERS)


def _belief(board: Board, thief: Coordinate, smell: dict):
    belief = uniform_belief(board.size, board.size)
    if smell:
        belief = apply_evidence(belief, scent_likelihood(smell, board))
    return choose_evasive_action(board, thief, belief)


def simulate(board: Board, cop: Coordinate, thief: Coordinate, policy, steps: int) -> int:
    scent = blank_field(board)
    for step in range(1, steps + 1):
        cop = _cop_pursues(board, cop, thief)
        scent = deposit(scent, board, cop)
        if cop == thief:
            return step - 1
        thief = resolve_move(board, thief, policy(board, thief, _observed(scent, board)), NO_BARRIERS)
        if cop == thief:
            return step
    return steps


def run_comparison(board: Board | None = None, steps: int = 35) -> dict:
    board = Board(size=7) if board is None else board
    blind = sum(simulate(board, cop, thief, _blind, steps) for cop, thief in SCENARIOS)
    belief = sum(simulate(board, cop, thief, _belief, steps) for cop, thief in SCENARIOS)
    return {"blind_total_survival": blind, "belief_total_survival": belief,
            "scenarios": len(SCENARIOS), "max_steps": steps}


def test_belief_driven_evasion_beats_the_blind_baseline() -> None:
    result = run_comparison()
    assert result["belief_total_survival"] > result["blind_total_survival"]
