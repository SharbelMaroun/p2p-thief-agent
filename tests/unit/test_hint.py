"""`M6-003e`: decode a natural-language hint into belief-space evidence.

Deterministic and coordinate-free: directional words become gradients over the grid, and
an unrecognised or absent hint carries no information rather than raising.
"""

import pytest

from p2p_thief_agent.perception.belief import BeliefError, uniform_belief
from p2p_thief_agent.perception.hint import decode_hint


def total(grid) -> float:
    return sum(v for row in grid for v in row)


def argmax(grid) -> tuple[int, int]:
    return max(((r, c) for r in range(len(grid)) for c in range(len(grid[0]))),
              key=lambda rc: grid[rc[0]][rc[1]])


def test_a_northward_hint_favours_the_top_rows() -> None:
    belief = decode_hint("I'm up north near the top", 3, 3)
    assert belief[0][0] > belief[2][0]
    assert total(belief) == pytest.approx(1.0)


def test_an_eastward_hint_favours_the_right_columns() -> None:
    belief = decode_hint("heading east", 3, 3)
    assert belief[0][2] > belief[0][0]


def test_a_westward_hint_favours_the_left_columns() -> None:
    belief = decode_hint("over to the west, on the left", 3, 3)
    assert belief[0][0] > belief[0][2]


def test_a_compound_direction_peaks_in_the_named_corner() -> None:
    """`north` × `east` gradients multiply, so the top-right cell is likeliest."""
    assert argmax(decode_hint("north east", 3, 3)) == (0, 2)


def test_a_centre_hint_peaks_in_the_middle() -> None:
    assert argmax(decode_hint("right in the middle", 3, 3)) == (1, 1)


def test_a_corner_hint_favours_the_corners_over_the_centre() -> None:
    belief = decode_hint("hiding in a corner", 3, 3)
    assert belief[0][0] > belief[1][1]


def test_conflicting_directions_pull_toward_the_axis_middle() -> None:
    belief = decode_hint("north and south at once", 3, 3)
    assert belief[1][0] > belief[0][0]


@pytest.mark.parametrize("opaque", ["hello there friend", "", "   ", None, 42])
def test_a_hint_with_no_cue_is_uniform(opaque: object) -> None:
    """Missing or opaque evidence is not an error — it is simply no information."""
    assert decode_hint(opaque, 3, 3) == uniform_belief(3, 3)


def test_a_degenerate_grid_is_rejected() -> None:
    with pytest.raises(BeliefError, match="at least 1x1"):
        decode_hint("north", 0, 3)
