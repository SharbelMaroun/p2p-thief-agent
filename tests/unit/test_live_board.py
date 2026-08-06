"""`M8-007` / `M8-007a` / `M8-007b`: the board, our own cell, and disclosed barriers.

Split from `test_live_view_model.py`, which covers the belief ramp and the turn banner.
The seam is real: those two decide what the *inference* looks like, these decide what the
*board* is allowed to contain — and `M8-007a` is a rule-15 question, not a rendering one.
"""

from __future__ import annotations

from p2p_thief_agent.live import TurnState, frame_of, local_truth


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


# --- M8-007 / M8-007a: the board ----------------------------------------------------------


def test_the_board_shows_our_own_cell_the_step_and_the_score() -> None:
    """Our marker is `T`, not `C` — this is the Thief's screen, and a mirrored copy of the
    companion repository's would label it backwards."""
    frame = frame_of(_truth(step=7, score=15))
    assert frame.at((3, 3)).is_own and frame.at((3, 3)).mark == "T"
    assert frame.status_line == "step 7   ·   score 15"


def test_only_disclosed_barriers_are_drawn() -> None:
    """`M8-007a`, on rule 15: a barrier is public *once declared*, so an undeclared one has
    no route onto the screen — it is not filtered out, it was never there."""
    frame = frame_of(_truth(disclosed_barriers=[(1, 1)]))
    assert frame.at((1, 1)).is_barrier and frame.at((1, 1)).mark == "#"
    assert not frame.at((2, 2)).is_barrier


def test_a_barrier_outranks_the_heat_so_it_cannot_be_hidden_under_colour() -> None:
    """An operator who cannot see a barrier will plan a move into it."""
    frame = frame_of(_truth(disclosed_barriers=[(1, 1)],
                            belief=_matrix(4, **{"1_1": 0.9})))
    assert frame.at((1, 1)).is_barrier and frame.at((1, 1)).colour == "#263238"


def test_visited_cells_are_marked_without_overriding_anything() -> None:
    frame = frame_of(_truth(visited=[(0, 1), (0, 2)]))
    assert frame.at((0, 1)).is_visited and not frame.at((0, 1)).is_barrier


def test_received_hints_are_shown_as_text() -> None:
    """`M8-007b`: a hint that never reaches the screen cannot be judged against the map."""
    frame = frame_of(_truth(hints=["I can hear you behind me", "Wrong street"]))
    assert frame.hints == ("I can hear you behind me", "Wrong street")


def test_the_frame_covers_every_cell_exactly_once() -> None:
    frame = frame_of(_truth(grid_size=5, own_position=(0, 0)))
    assert len(frame.cells) == 25
    assert len({view.cell for view in frame.cells}) == 25
