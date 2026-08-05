"""`M6-020`: when the Cop is provably adjacent, certainty collapses belief cleanly.

The emission centre is `0.9` on the Cop's own cell, so a `0.9` reading at an adjacent cell is
proof the Cop stands there. The belief must collapse onto that cell — a near-point-mass — yet
stay a valid distribution: it still sums to 1, never divides by zero, and drives a legal flee.
"""

import pytest

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.field import scent_likelihood
from p2p_thief_agent.strategy.belief_policy import believed_cop_cell, choose_evasive_action
from p2p_thief_agent.strategy.metrics import manhattan_distance

BOARD = Board(size=7)
THIEF = Coordinate(3, 3)
ADJACENT_COP = Coordinate(3, 2)  # the cell just west of the Thief


def test_certainty_collapses_the_belief_without_breaking_normalisation() -> None:
    belief = apply_evidence(uniform_belief(7, 7), scent_likelihood({(3, 2): 0.9}, BOARD))
    assert belief[3][2] == pytest.approx(1.0)  # collapsed onto the adjacent cell
    assert sum(v for row in belief for v in row) == pytest.approx(1.0)  # still a distribution
    assert believed_cop_cell(belief, BOARD) == ADJACENT_COP


def test_the_thief_flees_a_provably_adjacent_cop_with_a_legal_move() -> None:
    belief = apply_evidence(uniform_belief(7, 7), scent_likelihood({(3, 2): 0.9}, BOARD))
    action = choose_evasive_action(BOARD, THIEF, belief)
    assert action in legal_actions(BOARD, THIEF, frozenset())
    landed = resolve_move(BOARD, THIEF, action, frozenset())
    # Fleeing an adjacent Cop strictly increases distance from it.
    assert manhattan_distance(landed, ADJACENT_COP) > manhattan_distance(THIEF, ADJACENT_COP)
