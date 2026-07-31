"""`M5-014d`: Appendix F parameter policy, on its own.

`FIXED` values cannot change at all and `MINIMUM` values may move only in the
harder direction (rule 12). The statuses are pinned against this repository's
`docs/PARAMETERS_BASELINE.md`, which reads them from the book's tables 13, 15, 16,
and 18 -- so a silently edited constant fails here rather than at a match.
"""

import pytest

from p2p_thief_agent.protocol.agreement import (
    FIXED_TERMS,
    MINIMUM_TERMS,
    AgreementError,
    check_appendix_f,
)

TERMS = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.10, "emit_intensity": 0.9,
    "min_center_intensity": 0.05, "max_steps": 35, "barriers_max": 14,
    "setting": "New York", "hint_max_words": 15, "axis_origin_corner": "top-left",
    "axis_start_index": 0, "thief_start": [3, 3], "cop_start": [0, 0], "num_games": 6,
}


def test_appendix_f_statuses_match_the_parameters_baseline() -> None:
    """Pinned against `docs/PARAMETERS_BASELINE.md`, tables 13, 15, 16, and 18."""
    assert FIXED_TERMS == {
        "smell_grid_size": 5, "decay_per_step": 0.10, "emit_intensity": 0.9, "num_games": 6
    }
    assert MINIMUM_TERMS == {"board_size": 7, "max_steps": 35, "barriers_max": 14}


@pytest.mark.parametrize(
    ("term", "value"),
    [("smell_grid_size", 3), ("decay_per_step", 0.5), ("emit_intensity", 1.0), ("num_games", 1)],
)
def test_an_altered_fixed_value_is_refused(term: str, value: object) -> None:
    with pytest.raises(AgreementError, match=f"{term} is FIXED"):
        check_appendix_f({**TERMS, term: value})


@pytest.mark.parametrize(
    ("term", "value"), [("board_size", 6), ("max_steps", 34), ("barriers_max", 13)]
)
def test_a_weakened_minimum_is_refused(term: str, value: int) -> None:
    with pytest.raises(AgreementError, match=f"{term} is a MINIMUM"):
        check_appendix_f({**TERMS, term: value})


@pytest.mark.parametrize(
    ("term", "value"), [("board_size", 9), ("max_steps", 50), ("barriers_max", 20)]
)
def test_a_minimum_moved_in_the_harder_direction_is_allowed(term: str, value: int) -> None:
    check_appendix_f({**TERMS, term: value})


@pytest.mark.parametrize("value", [True, "7", 7.0, None])
def test_a_non_integer_minimum_is_refused(value: object) -> None:
    with pytest.raises(AgreementError, match="whole number"):
        check_appendix_f({**TERMS, "board_size": value})

