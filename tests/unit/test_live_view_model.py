"""`M8-001a` / `M8-001b` / `M8-011b`: the belief map and the turn banner.

The truth boundary is `test_local_truth_boundary.py` and the board itself is
`test_live_board.py`. Everything here is what the mandatory belief-map screenshot shows,
so it is pinned rather than eyeballed.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.live import TurnState, frame_of, heat_colour, local_truth
from p2p_thief_agent.live.view_model import BANNER_COLOURS


def _matrix(size: int, **cells: float):
    grid = [[0.0] * size for _ in range(size)]
    for key, value in cells.items():
        row, column = (int(part) for part in key.split("_"))
        grid[row][column] = value
    return grid


def _truth(**overrides):
    base = {"grid_size": 4, "own_position": (3, 3),
            "turn_state": TurnState.YOUR_TURN, "step": 3}
    return local_truth(**{**base, **overrides})


# --- M8-001a: deeper colour means higher probability ------------------------------------


def test_the_ramp_runs_white_to_deep_red() -> None:
    assert heat_colour(0.0, 1.0) == "#ffffff"
    assert heat_colour(1.0, 1.0) == "#ff3333"


def test_a_higher_probability_is_always_a_deeper_red() -> None:
    """The row's whole condition, asserted as a monotonic property rather than at two
    sample points."""
    channels = [int(heat_colour(p / 10, 1.0)[3:5], 16) for p in range(11)]
    assert channels == sorted(channels, reverse=True)
    assert len(set(channels)) > 5, "the ramp must actually vary, not step twice"


def test_the_ramp_is_relative_to_the_peak_not_absolute() -> None:
    """The decision worth defending. Belief spread over 64 cells peaks near 0.016, so an
    absolute ramp would render every honest board white and the map would never heat."""
    frame = frame_of(_truth(belief=_matrix(4, **{"1_1": 0.016, "2_2": 0.004})))
    assert frame.at((1, 1)).colour == "#ff3333", "the peak is always fully saturated"
    assert frame.at((2, 2)).colour != "#ffffff", "a quarter of the peak is still visible"


def test_a_board_with_no_belief_yet_stays_white_rather_than_dividing_by_zero() -> None:
    assert all(view.colour in ("#ffffff", "#e67e22") for view in frame_of(_truth()).cells)


def test_probability_is_clamped_so_a_bad_input_cannot_produce_a_broken_colour() -> None:
    """A value above the peak would compute a negative channel and emit a colour Tk
    refuses, taking the window down mid-match."""
    assert heat_colour(5.0, 1.0) == "#ff3333"


# --- M8-011b: colour is not the only signal ---------------------------------------------


def test_every_believed_cell_also_carries_a_percentage() -> None:
    frame = frame_of(_truth(belief=_matrix(4, **{"1_1": 0.5, "2_2": 0.25})))
    assert frame.at((1, 1)).percentage == "50%"
    assert frame.at((2, 2)).percentage == "25%"
    assert frame.at((0, 3)).percentage == "", "an unbelieved cell says nothing"


def test_a_belief_below_one_percent_reads_as_less_than_rather_than_zero() -> None:
    """Rounding a diffuse board to `0%` prints a claim that the police are nowhere, which
    is the opposite of what the number is there to say."""
    assert frame_of(_truth(belief=_matrix(4, **{"0_1": 0.004}))).at((0, 1)).percentage == "<1%"


def test_the_most_likely_cell_is_marked_with_text_as_well_as_colour() -> None:
    frame = frame_of(_truth(belief=_matrix(4, **{"1_2": 0.9, "0_3": 0.1})))
    assert frame.at((1, 2)).mark == "C?"
    assert frame.at((0, 3)).mark == ""


# --- M8-001b: the turn banner ------------------------------------------------------------


@pytest.mark.parametrize(
    ("state", "label", "accepts"),
    [
        (TurnState.YOUR_TURN, "YOUR TURN", True),
        (TurnState.LOCKED, "LOCKED", False),
        (TurnState.WAITING, "WAITING", False),
        (TurnState.GAME_OVER, "GAME OVER", False),
    ],
)
def test_each_banner_state_has_its_label_and_input_rule(
    state: TurnState, label: str, accepts: bool
) -> None:
    """Only `YOUR TURN` accepts input — locking is mandatory, and the interface "enforces
    the lock" to stop both sides acting on one turn."""
    frame = frame_of(_truth(turn_state=state))
    assert frame.banner_label == label
    assert frame.accepts_input is accepts


def test_the_two_states_the_book_names_are_green_and_grey() -> None:
    """`:1669`–`:1670`: a green `YOUR TURN` and a grey `LOCKED`."""
    assert BANNER_COLOURS[TurnState.YOUR_TURN] == "#2ecc71"
    assert BANNER_COLOURS[TurnState.LOCKED] == "#95a5a6"


def test_the_banner_explains_itself_in_words() -> None:
    assert frame_of(_truth()).banner_detail == "turn received (act enabled)"
    assert frame_of(_truth(turn_state=TurnState.LOCKED)).banner_detail == (
        "commit sent (input locked)"
    )
