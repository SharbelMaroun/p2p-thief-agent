"""The model-matched emitter decoder: exact where it must be, graceful where it can't (`M6-031`).

The pursuer grid is the motivation on record: raw-intensity belief scores 23/8/5
escapes across the archetypes and the decoded belief scores 24/24/24 — the whole
six-attempt graveyard was this estimator. These tests pin the properties that number
rests on.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.perception.emitter_decoder import (
    emitter_likelihood,
    match_error,
    residual,
)
from p2p_thief_agent.perception.field import blank_field, deposit
from p2p_thief_agent.perception.scent import emission_delta

BOARD = Board(size=7)


def observed(field) -> dict:
    return {(r, c): field[r][c] for r in range(BOARD.size)
            for c in range(BOARD.size) if field[r][c] > 0}


def argmax(grid) -> tuple[int, int]:
    return max(((r, c) for r in range(len(grid)) for c in range(len(grid[0]))),
               key=lambda rc: (grid[rc[0]][rc[1]], -rc[0], -rc[1]))


def test_the_residual_is_exactly_the_newest_stamp() -> None:
    """`τ' = (1−ρ)τ + Δ` with both terms non-negative: the clip never bites, so the
    residual recovers the stamp to floating-point precision."""
    first = deposit(blank_field(BOARD), BOARD, Coordinate(3, 3))
    second = deposit(first, BOARD, Coordinate(3, 4))
    delta = residual(observed(second), observed(first))
    for (row, col), value in delta.items():
        assert abs(value - emission_delta(row - 3, col - 4)) < 1e-9


def test_the_true_emitter_scores_zero_and_every_rival_scores_more() -> None:
    first = deposit(blank_field(BOARD), BOARD, Coordinate(2, 2))
    second = deposit(first, BOARD, Coordinate(2, 3))
    delta = residual(observed(second), observed(first))
    truth = match_error(BOARD, delta, (2, 3))
    assert truth < 1e-12
    for rival in ((2, 2), (2, 4), (1, 3), (3, 3), (0, 0)):
        assert match_error(BOARD, delta, rival) > 0.05


def test_the_decoder_tracks_a_whole_walk_exactly() -> None:
    """The decisive property: from turn one to the horizon, the likelihood argmax is
    the emitter's true cell, every single turn — including re-visited cells, where
    raw intensity weighting is exactly what loses the trail."""
    walk = [Coordinate(3, 3), Coordinate(3, 4), Coordinate(4, 4), Coordinate(4, 3),
            Coordinate(3, 3), Coordinate(3, 3), Coordinate(2, 3), Coordinate(2, 2)]
    field, previous = blank_field(BOARD), None
    for cell in walk:
        field = deposit(field, BOARD, cell)
        now = observed(field)
        grid = emitter_likelihood(BOARD, now, previous)
        assert argmax(grid) == (cell.row, cell.col)
        previous = now


def test_the_first_observation_alone_is_already_exact() -> None:
    field = deposit(blank_field(BOARD), BOARD, Coordinate(5, 1))
    assert argmax(emitter_likelihood(BOARD, observed(field), None)) == (5, 1)


def test_a_partial_window_decodes_with_the_trusted_intersection() -> None:
    """The live wire sends 5×5 windows, not the board. Restricting the score to
    cells both windows covered keeps the decode exact while the window moves."""
    first = deposit(blank_field(BOARD), BOARD, Coordinate(3, 3))
    second = deposit(first, BOARD, Coordinate(3, 4))

    def window(field, centre):
        return {(r, c): field[r][c]
                for r in range(centre.row - 2, centre.row + 3)
                for c in range(centre.col - 2, centre.col + 3)
                if 0 <= r < BOARD.size and 0 <= c < BOARD.size}

    now = window(second, Coordinate(3, 4))
    before = window(first, Coordinate(3, 3))
    trusted = set(now) & set(before)
    assert argmax(emitter_likelihood(BOARD, now, before, trusted)) == (3, 4)


def test_the_true_cell_dwarfs_its_best_rival_by_orders_of_magnitude() -> None:
    field = deposit(blank_field(BOARD), BOARD, Coordinate(4, 4))
    grid = emitter_likelihood(BOARD, observed(field), None)
    truth = grid[4][4]
    rivals = max(grid[r][c] for r in range(7) for c in range(7) if (r, c) != (4, 4))
    assert truth / rivals > 100


def test_a_physics_deviating_field_degrades_smoothly_not_fatally() -> None:
    """A rule-23 deviator emits something the model cannot explain; the belief must
    flatten toward uniform rather than crash or hard-commit (`M6-003c`)."""
    nonsense = {(0, 0): 3.0, (6, 6): 2.5, (3, 3): 9.9}
    grid = emitter_likelihood(BOARD, nonsense, None)
    assert sum(value for row in grid for value in row) > 0.0, "never a hard zero belief"
    assert len({value for row in grid for value in row}) == 1, (
        "inexplicable everywhere means no information, not a confident wrong answer")


def test_an_empty_observation_carries_no_information() -> None:
    grid = emitter_likelihood(BOARD, {}, None)
    assert len({value for row in grid for value in row}) == 1


def test_identical_inputs_give_identical_grids() -> None:
    field = deposit(blank_field(BOARD), BOARD, Coordinate(1, 5))
    assert emitter_likelihood(BOARD, observed(field), None) == \
        emitter_likelihood(BOARD, observed(field), None)
