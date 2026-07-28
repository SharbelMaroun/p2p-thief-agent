"""Unit tests for the pure positional metrics behind the Thief baseline policy."""

import pytest

from p2p_thief_agent.domain import Board, Coordinate, OriginCorner
from p2p_thief_agent.strategy.metrics import (
    edge_contacts,
    manhattan_distance,
    min_threat_distance,
    mobility,
    onward_reach,
)

BOARD = Board(size=7)


def test_manhattan_distance_is_symmetric_and_zero_on_self():
    a, b = Coordinate(1, 2), Coordinate(4, 6)
    assert manhattan_distance(a, b) == 7
    assert manhattan_distance(b, a) == 7
    assert manhattan_distance(a, a) == 0


def test_manhattan_distance_ignores_origin_corner():
    board = Board(size=7, origin_corner=OriginCorner.BOTTOM_RIGHT)
    assert board.contains(Coordinate(0, 0))
    assert manhattan_distance(Coordinate(0, 0), Coordinate(2, 3)) == 5


def test_min_threat_distance_picks_the_nearest_threat():
    threats = [Coordinate(0, 0), Coordinate(3, 4), Coordinate(6, 6)]
    assert min_threat_distance(Coordinate(3, 3), threats) == 1


def test_min_threat_distance_is_none_without_threats():
    assert min_threat_distance(Coordinate(3, 3), []) is None


def test_mobility_counts_four_escapes_in_the_interior():
    assert mobility(BOARD, Coordinate(3, 3)) == 4


def test_mobility_counts_two_escapes_in_a_corner():
    assert mobility(BOARD, Coordinate(0, 0)) == 2


def test_mobility_excludes_stay_and_respects_barriers():
    barriers = [Coordinate(2, 3), Coordinate(4, 3)]
    assert mobility(BOARD, Coordinate(3, 3), barriers) == 2


def test_mobility_is_zero_when_fully_enclosed():
    barriers = [Coordinate(0, 1), Coordinate(1, 0)]
    assert mobility(BOARD, Coordinate(0, 0), barriers) == 0


def test_onward_reach_sums_neighbour_mobility():
    # Centre of an open 7x7: four neighbours, each with four escapes.
    assert onward_reach(BOARD, Coordinate(3, 3)) == 16


def test_onward_reach_is_lower_at_a_corner_than_at_the_centre():
    assert onward_reach(BOARD, Coordinate(0, 0)) < onward_reach(BOARD, Coordinate(3, 3))


def test_onward_reach_is_zero_when_no_neighbour_is_reachable():
    barriers = [Coordinate(0, 1), Coordinate(1, 0)]
    assert onward_reach(BOARD, Coordinate(0, 0), barriers) == 0


def test_onward_reach_distinguishes_a_corridor_from_an_open_cell():
    # Walling both sides of (3, 3) leaves a north-south corridor.
    corridor = [Coordinate(3, 2), Coordinate(3, 4)]
    assert onward_reach(BOARD, Coordinate(3, 3), corridor) < onward_reach(BOARD, Coordinate(3, 3))


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        (Coordinate(0, 0), 2),
        (Coordinate(0, 6), 2),
        (Coordinate(6, 0), 2),
        (Coordinate(6, 6), 2),
        (Coordinate(0, 3), 1),
        (Coordinate(3, 6), 1),
        (Coordinate(3, 3), 0),
        (Coordinate(1, 1), 0),
    ],
)
def test_edge_contacts_classifies_corner_edge_and_interior(cell, expected):
    assert edge_contacts(BOARD, cell) == expected


def test_edge_contacts_honours_a_nonzero_axis_start_index():
    board = Board(size=5, axis_start_index=1)
    assert edge_contacts(board, Coordinate(1, 1)) == 2
    assert edge_contacts(board, Coordinate(3, 3)) == 0
