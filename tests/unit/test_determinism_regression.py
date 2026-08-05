"""`M6-028`: a stored golden action sequence guards against silent policy drift.

Determinism is a submission property. This pins the exact move the belief-driven policy makes
for a fixed sequence of believed Cop cells, so any change to the ranking, the tie-break, or
the metrics that silently altered the policy would break this test rather than slip into a
release unnoticed.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action

BOARD = Board(size=7)
HERE = Coordinate(3, 3)
# A fixed sequence of believed Cop cells (one "observation" per step).
COP_CELLS = [(0, 0), (6, 6), (3, 0), (0, 3), (6, 3)]
# The golden moves the current policy makes from (3, 3) for those cells.
EXPECTED_ACTIONS = ["S", "N", "N", "S", "N"]


def _peaked(row: int, col: int) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(1.0 if (r, c) == (row, col) else 0.0 for c in range(7)) for r in range(7))


def test_the_policy_reproduces_the_stored_action_sequence() -> None:
    actions = [choose_evasive_action(BOARD, HERE, _peaked(row, col)).value for row, col in COP_CELLS]
    assert actions == EXPECTED_ACTIONS
