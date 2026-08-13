"""The geometric localiser: exact on real windows, silent on anything else."""

from __future__ import annotations

import pytest

from p2p_thief_agent.domain.board import Board, OriginCorner
from p2p_thief_agent.perception.window_geometry import (
    certainty_belief,
    expected_window,
    window_centre,
)

BOARD = Board(7, OriginCorner.TOP_LEFT, 0)
EVERY_CELL = [(row, col) for row in range(7) for col in range(7)]


@pytest.mark.parametrize("cell", EVERY_CELL)
def test_locates_every_cell_from_a_full_window(cell: tuple[int, int]) -> None:
    assert window_centre(expected_window(*cell, BOARD), BOARD) == cell


@pytest.mark.parametrize("cell", EVERY_CELL)
def test_locates_from_keys_alone_when_every_value_is_zero(cell: tuple[int, int]) -> None:
    """A window of honest zeros is no evidence to a likelihood and a fix to geometry."""
    silent = dict.fromkeys(expected_window(*cell, BOARD), 0.0)
    assert window_centre(silent, BOARD) == cell


def test_refuses_a_window_with_its_zero_cells_omitted() -> None:
    assert window_centre({(3, 3): 0.9, (3, 4): 0.62, (2, 3): 0.62}, BOARD) is None


def test_refuses_a_ragged_grid() -> None:
    assert window_centre(expected_window(3, 3, BOARD) - {(2, 2)}, BOARD) is None


def test_refuses_an_empty_grid() -> None:
    assert window_centre({}, BOARD) is None


def test_refuses_a_window_wider_than_the_board() -> None:
    whole = {(row, col) for row in range(7) for col in range(7)}
    assert window_centre(whole, BOARD, half=4) is None


def test_certainty_belief_is_a_point_mass_on_the_located_cell() -> None:
    belief = certainty_belief((5, 2), BOARD)
    assert belief[5][2] == 1.0
    assert sum(sum(row) for row in belief) == 1.0
