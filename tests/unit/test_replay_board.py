"""The replay board reconstruction: both trails, tolerant of both log shapes (`M8-016`).

Rule 9's objective-board ban binds the live interface; the replay is the book's
"Retrospective Witness" and may draw what really happened. These tests pin the data the
widget draws: our trail up to the cursor, the opponent's aligned by step, barriers read
from either repository's payload shape, and a viewer that renders rather than raises on
a strange record.
"""

from p2p_thief_agent.replay.board import board_frame
from p2p_thief_agent.replay.load import parse_log


def _our_record(step: int, position: list[int]) -> dict:
    """Our shape: barriers live inside the sealed state string."""
    return {"commit": "c" * 64, "nonce": "n" * 32,
            "payload": {"step": step, "position": position,
                        "state": f"grid=7x7;self={position};barriers=[[6, 6]]"}}


def _their_record(step: int, position: list[int], barriers: list[list[int]]) -> dict:
    """The companion shape: a cumulative `barriers` list in the payload."""
    return {"commit": "c" * 64, "nonce": "n" * 32,
            "payload": {"step": step, "position": position, "barriers": barriers,
                        "state": "grid=7x7"}}


OURS = parse_log({"game_id": "g", "records": [
    _our_record(1, [3, 3]),
    _our_record(2, [3, 4]),
    _our_record(3, [3, 5]),
]}, origin="ours")

THEIRS = parse_log({"game_id": "g", "records": [
    _their_record(1, [0, 0], []),
    _their_record(2, [0, 1], []),
    _their_record(3, [0, 1], [[1, 1]]),
]}, origin="theirs")


def test_our_trail_grows_with_the_cursor() -> None:
    assert board_frame(OURS, 0).ours.cells == ((3, 3),)
    frame = board_frame(OURS, 2)
    assert frame.ours.cells == ((3, 3), (3, 4), (3, 5))
    assert frame.ours.current == (3, 5)


def test_barriers_are_read_from_both_log_shapes() -> None:
    """Ours sit in the state string; the companion's in a cumulative payload list.
    The board shows the union, so the reconstruction matches what both sides knew."""
    frame = board_frame(OURS, 2, opponent=THEIRS)
    assert (6, 6) in frame.barriers, "parsed out of our state string"
    assert (1, 1) in frame.barriers, "the companion-shaped cumulative list"


def test_the_opponent_trail_aligns_by_step() -> None:
    frame = board_frame(OURS, 1, opponent=THEIRS)
    assert frame.theirs.cells == ((0, 0), (0, 1)), "steps 1..2 only, matching the cursor"
    assert board_frame(OURS, 1).theirs.cells == (), "no opponent log, no invented trail"


def test_grid_size_comes_from_the_state_string() -> None:
    assert board_frame(OURS, 0).grid_size == 7


def test_capture_rings_only_the_final_step() -> None:
    """The ringed cell is ours: the cell we were caught on is the audit's subject."""
    assert board_frame(OURS, 2, captured=True).capture_cell == (3, 5)
    assert board_frame(OURS, 1, captured=True).capture_cell is None


def test_a_damaged_record_renders_rather_than_raises() -> None:
    log = parse_log({"records": [
        {"commit": "c" * 64, "nonce": "n" * 32, "payload": {"step": 1}},
        {"commit": "c" * 64, "nonce": "n" * 32,
         "payload": {"step": 2, "position": [4, 4], "barriers": "not-a-list"}},
    ]}, origin="damaged")
    frame = board_frame(log, 1)
    assert frame.ours.cells == ((4, 4),), "the positionless and malformed parts are skipped"
    assert frame.barriers == frozenset()
    assert frame.grid_size == 7


def test_the_caption_reports_what_is_actually_drawn() -> None:
    with_theirs = board_frame(OURS, 2, opponent=THEIRS).caption
    assert "police trail 3 step(s)" in with_theirs
    assert "opponent log not loaded" in board_frame(OURS, 2).caption
