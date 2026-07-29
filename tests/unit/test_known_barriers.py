"""Unit tests for M3-002 known-disclosed-barrier tracking with provenance."""

import pytest

from p2p_thief_agent.domain import Board, Coordinate, DomainError
from p2p_thief_agent.state.known_barriers import KnownBarriers

BOARD = Board(size=7)


def test_records_provenance_step():
    kb = KnownBarriers().record(BOARD, Coordinate(2, 2), step=3)
    assert kb.blocks(Coordinate(2, 2))
    assert kb.disclosed_at(Coordinate(2, 2)) == 3
    assert kb.cells == frozenset({Coordinate(2, 2)})


def test_unknown_cell_has_no_provenance():
    kb = KnownBarriers().record(BOARD, Coordinate(2, 2), step=3)
    assert not kb.blocks(Coordinate(4, 4))
    assert kb.disclosed_at(Coordinate(4, 4)) is None


def test_recording_is_immutable():
    original = KnownBarriers()
    extended = original.record(BOARD, Coordinate(1, 1), step=0)
    assert original.cells == frozenset()
    assert extended.cells == frozenset({Coordinate(1, 1)})


def test_earliest_disclosure_step_is_kept():
    kb = (
        KnownBarriers()
        .record(BOARD, Coordinate(2, 2), step=5)
        .record(BOARD, Coordinate(2, 2), step=2)
    )
    assert kb.disclosed_at(Coordinate(2, 2)) == 2
    assert len(kb.items) == 1


def test_later_disclosure_does_not_overwrite_earlier_step():
    kb = (
        KnownBarriers()
        .record(BOARD, Coordinate(2, 2), step=2)
        .record(BOARD, Coordinate(2, 2), step=5)
    )
    assert kb.disclosed_at(Coordinate(2, 2)) == 2
    assert len(kb.items) == 1


def test_off_board_barrier_rejected():
    with pytest.raises(DomainError):
        KnownBarriers().record(BOARD, Coordinate(7, 7), step=1)


def test_record_all_shares_the_disclosure_step():
    cells = [Coordinate(0, 0), Coordinate(0, 1)]
    kb = KnownBarriers().record_all(BOARD, cells, step=4)
    assert kb.disclosed_at(Coordinate(0, 0)) == 4
    assert kb.disclosed_at(Coordinate(0, 1)) == 4


def test_ordering_is_deterministic_by_cell():
    kb = KnownBarriers().record_all(
        BOARD, [Coordinate(3, 1), Coordinate(0, 5), Coordinate(0, 2)], step=1
    )
    ordered_cells = [cell for cell, _ in kb.items]
    assert ordered_cells == [Coordinate(0, 2), Coordinate(0, 5), Coordinate(3, 1)]


def test_negative_step_rejected():
    with pytest.raises(DomainError):
        KnownBarriers(((Coordinate(1, 1), -1),))


def test_non_coordinate_entry_rejected():
    with pytest.raises(DomainError):
        KnownBarriers((((1, 1), 0),))


def test_equal_records_are_equal_and_hashable():
    a = KnownBarriers().record(BOARD, Coordinate(2, 2), step=1)
    b = KnownBarriers().record(BOARD, Coordinate(2, 2), step=1)
    assert a == b
    assert hash(a) == hash(b)
