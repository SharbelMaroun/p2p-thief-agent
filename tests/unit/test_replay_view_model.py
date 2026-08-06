"""`M8-006` / `M8-006a` / `M8-008b`: the screen as data, so it can be asserted.

A Tk window cannot be checked in CI, so the screenshot in the README would otherwise rest
on someone having looked at it once. Everything the picture claims is decided here: the
stamp text, its colour, which row is marked bad, and what the detail panel shows.

That the stored images stay regenerable is `test_replay_screenshots.py` (`M8-015d`).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from p2p_thief_agent.replay import Replay, Verdict, frame_of, load_log, parse_log

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "replay"


def _replay(name: str) -> Replay:
    return Replay(load_log(FIXTURES / name))


# --- M8-006 / M8-006a: read-only, display-ready ------------------------------------------


def test_the_frame_is_frozen_so_rendering_cannot_write_back() -> None:
    """`M8-006a`: "the view cannot mutate game state" — guaranteed by the type."""
    frame = frame_of(_replay("log_verified_ok.json"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        frame.stamp = "Verified OK"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        frame.rows[0].move = "N"  # type: ignore[misc]


def test_every_field_a_widget_reads_is_a_string_or_a_primitive() -> None:
    """`M8-006`: "no widget touches domain or protocol code directly". A domain object in
    the frame would be a handle a widget could reach through."""
    for row in frame_of(_replay("log_verified_ok.json")).rows:
        for field in dataclasses.fields(row):
            assert isinstance(getattr(row, field.name), (str, int, bool)), field.name


def test_the_screen_carries_the_nonce_move_and_commit_the_book_requires() -> None:
    """Asked directly: the viewer must display "the nonce, move, and the original commit
    hash from the log entry" (p.56/142) — in full, because a screenshot has to be
    checkable, with the short form kept for the list."""
    row = frame_of(_replay("log_verified_ok.json")).current
    assert len(row.commit) == 64 and len(row.nonce) == 32
    assert row.move in {"N", "S", "E", "W"}
    assert row.commit_short.endswith("…") and len(row.commit_short) < len(row.commit)


def test_a_record_missing_its_fields_still_renders() -> None:
    """A viewer that dies on a malformed log shows nothing where it should show
    `TAMPERED`, which is the worst possible failure for this screen (`M8-008c`)."""
    frame = frame_of(Replay(parse_log(
        {"records": [{"step": 1, "nonce": "a" * 32}, {"nonce": "b" * 32}]}
    )))
    assert frame.stamp == Verdict.TAMPERED.value
    assert frame.rows[1].commit == "—" and frame.rows[1].move == "—"


def test_a_record_that_is_not_an_object_at_all_still_renders() -> None:
    frame = frame_of(Replay(parse_log(
        {"records": [{"step": 1, "nonce": "a" * 32}, "not a record"]}
    )))
    assert len(frame.rows) == 2 and not frame.rows[1].ok
    assert frame.rows[1].step == "?" and frame.rows[1].commit == "—"


# --- M8-008b: the per-step verdict beside the match verdict ------------------------------


def test_each_row_carries_its_own_verdict_and_reason() -> None:
    """"Operator sees where a match failed" — the match banner alone cannot say which
    step, and that is the only question left once `:1769` has decided the match."""
    rows = frame_of(_replay("log_tampered.json")).rows
    bad = next(row for row in rows if not row.ok)
    assert bad.verdict == "TAMPERED" and "commitment rejected" in bad.reason
    assert all("matches commit" in row.reason for row in rows if row.ok)


def test_the_cursor_row_is_flagged_and_follows_navigation() -> None:
    replay = _replay("log_verified_ok.json")
    replay.go_to(3)
    frame = frame_of(replay)
    assert [row.is_current for row in frame.rows].count(True) == 1
    assert frame.current.index == 3 and frame.position_label == "step 4 of 8"


def test_the_frame_reports_the_sequence_summary_separately_from_the_stamp() -> None:
    """Matches the `U-026` decision: structural findings are reported beside the verdict,
    never folded into it."""
    frame = frame_of(_replay("log_verified_ok.json"))
    assert frame.sequence_ok and "sequence intact" in frame.sequence_summary


def test_the_frame_names_the_file_it_came_from() -> None:
    """A verification screenshot that does not say which log was verified is evidence of
    nothing in particular — and rule 36's audit covers two of them."""
    frame = frame_of(_replay("log_verified_ok.json"))
    assert frame.origin.endswith("log_verified_ok.json")
    assert frame.game_id == "demo-vs-rival" and frame.sub_game == "2"
