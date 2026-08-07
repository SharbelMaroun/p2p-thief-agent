"""`M8-015` / `M8-015b` / `M8-015c` / `M8-015d`: the stored screenshots stay regenerable.

The book calls a `Verified OK` capture "absolute mandatory" in the README report
(p.81/189). The images in `assets/` are produced by
`scripts/capture_replay_screenshots.py` from the two committed fixtures, so `M8-015d`'s
condition — "a grader can regenerate them" — holds only while those fixtures still produce
those verdicts. That is what this module pins.

Only `Verified OK` is mandatory. The `TAMPERED` capture (`M8-015c`) is ours: a viewer shown
only passing is a viewer that might not be checking anything.
"""

from __future__ import annotations

import json
from pathlib import Path

from p2p_thief_agent.replay import Replay, frame_of, load_log, parse_log
from p2p_thief_agent.replay.view_model import COLOUR_OK, COLOUR_TAMPERED, stamp_is_green

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "replay"
ASSETS = Path(__file__).resolve().parents[2] / "assets"
PNG_MAGIC = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])


def _replay(name: str) -> Replay:
    return Replay(load_log(FIXTURES / name))


# --- M8-015d: the images are a function of committed fixtures ---------------------------


def test_the_verified_fixture_still_produces_a_green_stamp() -> None:
    """The assertion the mandatory `Verified OK` screenshot rests on (p.81/189)."""
    frame = frame_of(_replay("log_verified_ok.json"))
    assert frame.stamp == "Verified OK"
    assert frame.stamp_colour == COLOUR_OK
    assert stamp_is_green(frame)
    assert frame.banner == "Verified OK — 8 steps re-verified"
    assert all(row.ok for row in frame.rows)


def test_the_tampered_fixture_still_names_step_six() -> None:
    """Not a mandatory submission item — asked directly, only `Verified OK` is — but a
    viewer shown only passing is a viewer that might check nothing."""
    replay = _replay("log_tampered.json")
    replay.go_to_first_divergence()
    frame = frame_of(replay)

    assert frame.stamp == "TAMPERED"
    assert frame.stamp_colour == COLOUR_TAMPERED
    assert not stamp_is_green(frame)
    assert frame.current.step == "6" and not frame.current.ok
    assert [row.ok for row in frame.rows].count(False) == 1


def test_both_fixtures_are_valid_json_the_loader_accepts() -> None:
    for name in ("log_verified_ok.json", "log_tampered.json"):
        assert parse_log(json.loads((FIXTURES / name).read_text("utf-8"))).records, name


def test_both_stored_images_exist_and_are_real_pngs() -> None:
    """The images are committed evidence. A missing, truncated or non-image file is a
    submission defect that would otherwise surface only when a grader opened the README."""
    for name in ("replay-verified-ok.png", "replay-tampered.png"):
        image = ASSETS / name
        assert image.exists(), f"{name} is missing; run scripts/capture_replay_screenshots.py"
        assert image.stat().st_size > 5_000, f"{name} is suspiciously small"
        assert image.read_bytes()[:8] == PNG_MAGIC, f"{name} is not a PNG"
