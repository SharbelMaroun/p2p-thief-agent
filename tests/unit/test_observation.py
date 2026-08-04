"""`M6-002`: consume and produce the public `smell_grid` observation.

The wire shape is fixed by `SIM_WIRE_PROTOCOL.md`: a sparse `{"r,c": intensity}` map.
These cover the shape, the sparse "absent, not zero" rule, deterministic ordering, and
the boundary/rejection cases a hostile or buggy peer would hit.
"""

import pytest

from p2p_thief_agent.perception.observation import (
    ObservationError,
    encode_smell_grid,
    parse_smell_grid,
)


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
        {"-1,0": 0.9},        # negative coordinate
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
