"""`M8-012` / `M8-012a`: the replay app verifies a log this repository did not write.

**This is the file that decides whether the replay app means anything.** A verifier fed
only its own output confirms that our writer and our reader agree, which they always will;
it would pass every other test here while being useless at the audit table.

Rule 36 mandates a "comprehensive mutual log audit" at the end of every match as a
necessary condition for agreement (p.131/276), and p.39/102: "each side presents its full
log … each side reconstructs the opponent's data through the revealed nonces". The
reference agrees in code, auto-locating `logs/<opponent_group_id>/log_<game_id>_gNN.json`.

Detection of a *forged* foreign log is `test_foreign_log_tampered.py`.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from p2p_thief_agent.replay import LogNotReplayableError, Replay, Verdict, load_log
from tests.integration.foreign_log_writer import foreign_writer, write_foreign_log

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "replay"


def test_a_log_written_by_a_stranger_verifies(tmp_path: Path) -> None:
    """The headline. Nothing in this log came from our writer."""
    replay = Replay(load_log(write_foreign_log(tmp_path, foreign_writer(6))))
    assert replay.stamp is Verdict.VERIFIED_OK
    assert replay.total == 6
    assert replay.banner == "Verified OK — 6 steps re-verified"


def test_a_foreign_shape_is_tolerated_where_it_does_not_affect_verification(
    tmp_path: Path,
) -> None:
    """An unknown `schema_version`, extra keys, and `sub_game` for `sub_game_number`.
    Refusing on any of those would fail rule 36 on a cosmetic difference and hand a real
    forger the excuse that our viewer could not open the evidence."""
    log = load_log(write_foreign_log(tmp_path, foreign_writer(3)))
    assert log.sub_game == 2 and log.game_id == "rival-vs-us"
    assert "their_own_extra_field" in log.records[0]


def test_navigation_and_sequence_reporting_work_on_the_foreign_log(tmp_path: Path) -> None:
    replay = Replay(load_log(write_foreign_log(tmp_path, foreign_writer(4))))
    assert replay.go_to_step(3) == 2
    assert replay.step_back() == 1 and replay.check.ok
    assert replay.sequence.contiguous


def test_the_origin_is_carried_so_a_screenshot_says_whose_log_it_was(tmp_path: Path) -> None:
    """A mutual audit produces two banners; a screenshot of one that does not name its
    file is evidence of nothing in particular."""
    path = write_foreign_log(tmp_path, foreign_writer(2), name="log_rival-vs-us_g02.json")
    assert load_log(path).origin.endswith("log_rival-vs-us_g02.json")


def test_the_replay_package_never_imports_our_identity_or_output_location() -> None:
    """Structural, because the bug is silent: a loader consulting our `game_id`, our keys,
    or our artifacts directory would still pass every test above while quietly being unable
    to open a real opponent's file at the audit.

    `protocol.crypto` is the one permitted dependency — the construction is shared by
    definition, and re-implementing it here would verify our copy against our copy.
    """
    allowed = ("p2p_thief_agent.protocol.crypto", "p2p_thief_agent.replay")
    for module in sorted(SRC.glob("*.py")):
        tree = ast.parse(module.read_text("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("p2p_thief"):
                assert (node.module or "").startswith(allowed), (
                    f"{module.name} imports {node.module}; the replay verifier must not "
                    "depend on our own identity, config, or output location [M8-012]"
                )


# --- M8-008c: a malformed log must not crash the viewer ---------------------------------


def test_a_missing_opponent_log_is_a_reportable_state_not_a_crash(tmp_path: Path) -> None:
    """An opponent who has not sent theirs yet is normal, and the viewer says so."""
    with pytest.raises(LogNotReplayableError, match="cannot be read"):
        load_log(tmp_path / "log_they_never_sent.json")


def test_a_truncated_opponent_file_is_reported_as_such(tmp_path: Path) -> None:
    path = tmp_path / "half.json"
    path.write_text(json.dumps(foreign_writer(3))[:200], "utf-8")
    with pytest.raises(LogNotReplayableError, match="not valid JSON"):
        load_log(path)


@pytest.mark.parametrize(
    ("document", "expected"),
    [
        ([{"step": 1}], "top level is not a JSON object"),
        ("just a string", "top level is not a JSON object"),
        ({"summary": {"outcome": "capture"}}, "no `records` array"),
        ({"records": []}, "no `records` array"),
        ({"records": "1,2,3"}, "no `records` array"),
    ],
)
def test_a_document_that_is_not_a_log_is_refused_with_the_reason(
    tmp_path: Path, document: object, expected: str
) -> None:
    """`M8-008c`. Each of these could arrive at a real audit — a bare array, a config sent
    by mistake, an emptied log. None may reach the verifier and come back with a verdict,
    because "no records found" and "the records verify" are different claims and only one
    of them belongs on a submission screenshot."""
    path = tmp_path / "odd.json"
    path.write_text(json.dumps(document), "utf-8")
    with pytest.raises(LogNotReplayableError, match=expected):
        load_log(path)


def test_a_directory_of_both_sides_logs_verifies_each_independently(tmp_path: Path) -> None:
    """What the mutual audit actually looks like: ours and theirs, same code path, verdict
    reached separately for each."""
    for name, game in (("log_us_g01.json", "us"), ("log_them_g01.json", "them")):
        write_foreign_log(tmp_path, foreign_writer(3, game=game), name=name)
    stamps = {p.name: Replay(load_log(p)).stamp for p in sorted(tmp_path.glob("log_*.json"))}
    assert set(stamps.values()) == {Verdict.VERIFIED_OK} and len(stamps) == 2
