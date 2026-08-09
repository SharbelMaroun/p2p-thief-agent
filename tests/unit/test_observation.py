"""`M6-002`: consume and produce the public `smell_grid` observation.

The wire shape is fixed by `SIM_WIRE_PROTOCOL.md`: a sparse `{"r,c": intensity}` map.
These cover the shape, the sparse "absent, not zero" rule, deterministic ordering, and
the boundary/rejection cases a hostile or buggy peer would hit.
"""

import pytest

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.perception.observation import (
    SCENT_PRECISION,
    ObservationError,
    encode_smell_grid,
    parse_smell_grid,
    parse_smell_grid_dropped_count,
)

BOARD = Board(size=7)


def test_it_parses_the_wire_shape_into_a_cell_map() -> None:
    assert parse_smell_grid({"0,0": 0.9, "3,2": 0.14}) == {(0, 0): 0.9, (3, 2): 0.14}


def test_parsing_is_order_independent() -> None:
    """A map is a map: whatever order the keys arrive in, the result is the same."""
    forward = parse_smell_grid({"0,0": 0.9, "1,1": 0.2})
    reverse = parse_smell_grid({"1,1": 0.2, "0,0": 0.9})
    assert forward == reverse == {(0, 0): 0.9, (1, 1): 0.2}


def test_an_empty_observation_is_an_empty_map() -> None:
    assert parse_smell_grid({}) == {}


def test_encoding_omits_silent_cells_rather_than_zero_filling() -> None:
    """`M6-006a`: an unseen cell is absent, not a zero entry."""
    assert encode_smell_grid({(0, 0): 0.9, (1, 1): 0.0, (2, 2): 0.14}) == {"0,0": 0.9, "2,2": 0.14}


def test_encoding_emits_keys_in_a_deterministic_order() -> None:
    grid = encode_smell_grid({(2, 2): 0.14, (0, 0): 0.9, (0, 1): 0.62})
    assert list(grid) == ["0,0", "0,1", "2,2"]


def test_a_field_round_trips_through_the_wire_form() -> None:
    field = {(0, 0): 0.9, (1, 2): 0.62, (4, 4): 0.04}
    assert parse_smell_grid(encode_smell_grid(field)) == field


@pytest.mark.parametrize(
    "bad",
    [
        {0: 0.9},             # key is not a string at all
        {"0": 0.9},           # key is not "r,c"
        {"0,1,2": 0.9},       # three parts
        {"a,b": 0.9},         # non-integer coordinates
        {"0,0": "hot"},       # non-numeric intensity
        {"0,0": -0.1},        # negative intensity
        {"0,0": True},        # a bool is not an intensity
    ],
)
def test_a_malformed_grid_is_rejected_by_name(bad: dict) -> None:
    with pytest.raises(ObservationError):
        parse_smell_grid(bad)


def test_a_non_object_grid_is_rejected() -> None:
    with pytest.raises(ObservationError, match="must be an object"):
        parse_smell_grid([("0,0", 0.9)])


def test_an_on_board_cell_is_accepted_against_the_negotiated_grid() -> None:
    assert parse_smell_grid({"6,6": 0.14}, BOARD) == {(6, 6): 0.14}


def test_an_off_board_cell_is_dropped_not_rejected_against_the_negotiated_grid() -> None:
    """`M6-006b`, corrected 2026-08-09: a fixed-size window from a sender near an edge
    necessarily carries an off-board cell; that is a different encoding convention, not
    evidence of a hostile peer, so only the impossible cell is dropped."""
    assert parse_smell_grid({"6,6": 0.9, "7,0": 0.9}, BOARD) == {(6, 6): 0.9}


def test_a_negative_coordinate_is_structurally_valid_without_a_board() -> None:
    """A negative coordinate is off-board only relative to a board's axis_start_index;
    with no board to judge against, it is not malformed data."""
    assert parse_smell_grid({"-1,0": 0.9}) == {(-1, 0): 0.9}


def test_a_negative_coordinate_is_dropped_like_any_off_board_cell_with_a_board() -> None:
    assert parse_smell_grid({"-1,0": 0.9, "0,0": 0.9}, BOARD) == {(0, 0): 0.9}


def test_a_realistic_corner_centred_fixed_size_window_keeps_only_the_on_board_cells() -> None:
    """The exact reproduction: a foreign encoder's 5x5 window centred on an opponent
    standing at the (0,0) corner, absolute board coordinates. Only the 3x3 on-board
    intersection survives; the match is never blinded by this."""
    window = {f"{r},{c}": 0.1 for r in range(-2, 3) for c in range(-2, 3)}
    kept = parse_smell_grid(window, BOARD)
    assert set(kept) == {(r, c) for r in range(3) for c in range(3)}
    assert len(kept) == 9


def test_the_dropped_count_reports_how_many_cells_were_off_board() -> None:
    """The count stays visible even though the cells themselves are silently dropped, so
    a grid that is mostly or entirely off-board (a real encoding mismatch) is observable."""
    window = {f"{r},{c}": 0.1 for r in range(-2, 3) for c in range(-2, 3)}
    assert parse_smell_grid_dropped_count(window, BOARD) == 25 - 9


def test_a_wholly_off_board_grid_parses_empty_with_a_nonzero_dropped_count() -> None:
    grid = {"-5,-5": 0.9, "-4,-5": 0.9}
    assert parse_smell_grid(grid, BOARD) == {}
    assert parse_smell_grid_dropped_count(grid, BOARD) == 2


def test_the_dropped_count_is_zero_for_a_fully_on_board_grid() -> None:
    assert parse_smell_grid_dropped_count({"3,3": 0.9}, BOARD) == 0


def test_encoding_rounds_to_the_pinned_precision() -> None:
    """`M6-006c`: two fields differing below the precision serialise to identical bytes."""
    noisy = {(0, 0): 0.5 + 10 ** -(SCENT_PRECISION + 2)}
    assert encode_smell_grid(noisy) == encode_smell_grid({(0, 0): 0.5}) == {"0,0": 0.5}


def test_a_below_precision_intensity_is_omitted_as_silent() -> None:
    assert encode_smell_grid({(0, 0): 10 ** -(SCENT_PRECISION + 2)}) == {}


def test_the_wire_form_is_idempotent_under_re_encoding() -> None:
    """`M6-006`: a field survives the round trip without precision drift."""
    field = {(0, 0): 0.9, (3, 4): 0.020000, (6, 6): 0.04}
    once = encode_smell_grid(field)
    assert encode_smell_grid(parse_smell_grid(once, BOARD)) == once
