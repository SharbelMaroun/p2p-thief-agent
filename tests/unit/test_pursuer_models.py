"""The committed pursuer archetypes: deterministic, legal, and harness-identical (`M6-029`).

The research report's stronger-Cop numbers came from scratch code that no longer
exists; these tests pin the committed replacements so every grid row stays
reproducible.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.strategy.metrics import manhattan_distance
from p2p_thief_agent.strategy.pursuer_models import (
    PURSUERS,
    anticipating_step,
    greedy_step,
    herding_step,
)
from tests.unit.test_strategy_comparison import _cop_pursues

BOARD = Board(size=7)


def test_greedy_is_the_harness_cop_exactly() -> None:
    """One brain, one place: the model and `simulate`'s pursuer must never drift."""
    for cop, thief in [(Coordinate(0, 0), Coordinate(6, 6)),
                       (Coordinate(3, 0), Coordinate(3, 6)),
                       (Coordinate(5, 5), Coordinate(4, 4))]:
        assert greedy_step(BOARD, cop, thief) == _cop_pursues(BOARD, cop, thief)


def test_every_model_returns_a_cell_one_legal_step_away() -> None:
    barriers = frozenset({Coordinate(2, 3)})
    for model in PURSUERS.values():
        target = model(BOARD, Coordinate(2, 2), Coordinate(5, 5), barriers)
        assert manhattan_distance(target, Coordinate(2, 2)) <= 1
        assert target not in barriers
        BOARD.validate_position(target)


def test_models_are_deterministic() -> None:
    args = (BOARD, Coordinate(1, 4), Coordinate(5, 2), frozenset())
    for model in PURSUERS.values():
        assert model(*args) == model(*args)


def test_on_the_open_interior_all_three_close_like_greedy() -> None:
    """Far from walls the flight set is symmetric and the refinements decay to the
    reference shape — the differences only appear where captures happen."""
    cop, thief = Coordinate(6, 3), Coordinate(2, 3)
    expected = greedy_step(BOARD, cop, thief)
    assert herding_step(BOARD, cop, thief) == expected
    assert anticipating_step(BOARD, cop, thief) == expected


def test_all_three_gain_ground_every_turn() -> None:
    for model in PURSUERS.values():
        cop, thief = Coordinate(0, 0), Coordinate(4, 5)
        target = model(BOARD, cop, thief)
        assert manhattan_distance(target, thief) < manhattan_distance(cop, thief)


def test_the_classification_order_starts_with_the_reference_shape() -> None:
    """Ties resolve to the simplest pursuer — the one a classmate most likely runs."""
    assert list(PURSUERS) == ["greedy", "herding", "anticipating"]
