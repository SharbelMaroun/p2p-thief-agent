"""`M6-021`: the first turn has no observation, but the agreed start is public.

Belief does not begin uniform: the Cop's start cell is public and this peer moves first, so
on turn 1 the Cop is exactly there — a point mass the Thief flees from the very first move.
"""

import pytest

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate, DomainError
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.belief_policy import (
    believed_cop_cell,
    choose_evasive_action,
    initial_belief,
)
from p2p_thief_agent.strategy.metrics import manhattan_distance

BOARD = Board(size=7)
COP_START = Coordinate(0, 0)
THIEF = Coordinate(3, 3)


def test_belief_begins_at_the_public_cop_start() -> None:
    belief = initial_belief(BOARD, COP_START)
    assert belief[0][0] == 1.0
    assert sum(v for row in belief for v in row) == pytest.approx(1.0)
    assert believed_cop_cell(belief, BOARD) == COP_START


def test_the_first_move_flees_the_known_cop_start() -> None:
    action = choose_evasive_action(BOARD, THIEF, initial_belief(BOARD, COP_START))
    assert action in legal_actions(BOARD, THIEF, frozenset())
    landed = resolve_move(BOARD, THIEF, action, frozenset())
    assert manhattan_distance(landed, COP_START) > manhattan_distance(THIEF, COP_START)


def test_an_off_board_start_is_rejected() -> None:
    with pytest.raises(DomainError):
        initial_belief(BOARD, Coordinate(9, 9))
