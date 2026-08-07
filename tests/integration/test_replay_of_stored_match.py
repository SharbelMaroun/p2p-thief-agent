"""`M9-013c`: the replay app re-verifies a match read back off disk.

Every other replay test builds records in memory and hands them to the verifier. This one
closes the loop the *grader* will close: a series is played, its artifacts are written as
JSON, the file is loaded from disk by path, and the verifier reaches `Verified OK` without
ever seeing the objects that produced it.

The distance matters. `json.dumps` and `json.loads` are not identity — an int key becomes a
string, a tuple becomes a list, a `Decimal` becomes something else entirely — and the
commitment is over canonical bytes. A verifier that only ever sees in-memory dicts can pass
forever while every stored log fails, and the first person to notice would be whoever opened
the submission.

The screenshot of this state is **absolute mandatory** (p.81/189: "from the Live GUI... and
from the Replay App demonstrating Verified OK"), and rule 20 makes a verifying replay a
threshold condition. So this is the row that decides whether the submission has evidence at
all, not merely whether the code is correct.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.replay.load import load_log
from p2p_thief_agent.replay.verify import Verdict, verify_records
from tests.integration.rehearsal import rehearse
from tests.integration.rehearsal_fixtures import OUR_GROUP


@pytest.fixture(scope="module")
def stored(tmp_path_factory):
    """A rehearsed series, written to disk exactly as a counted game would be."""
    return rehearse(tmp_path_factory.mktemp("stored"))


def log_paths(stored) -> list:
    return sorted(path for name, path in stored.written.items() if name.startswith("log_"))


def test_the_series_wrote_a_log_file_per_sub_game(stored) -> None:
    assert log_paths(stored), "no log artifact reached disk"


def test_every_stored_log_loads_from_its_path_alone(stored) -> None:
    """`load_log` takes a path and nothing else — the mutual-audit posture of rule 36. An
    opponent hands over a file, not a Python object."""
    for path in log_paths(stored):
        assert load_log(path).records


def test_every_stored_log_re_verifies_to_verified_ok(stored) -> None:
    """**The row.** Read off disk, re-hashed, compared to the stored commitments."""
    for path in log_paths(stored):
        verdict = verify_records(load_log(path).records)
        assert verdict.verdict is Verdict.VERIFIED_OK, f"{path.name}: {verdict.banner}"


def test_the_banner_says_verified_ok_and_counts_the_steps(stored) -> None:
    """The banner is what the mandatory screenshot shows, so its text is part of the
    evidence rather than a debug aid."""
    banner = verify_records(load_log(log_paths(stored)[0]).records).banner
    assert banner.startswith(Verdict.VERIFIED_OK.value)
    assert "re-verified" in banner


def test_a_byte_changed_on_disk_is_detected_after_reloading(stored, tmp_path) -> None:
    """Proves the round trip verifies rather than merely parses. The tamper is applied to
    the **file**, so nothing in memory could be carrying the original past the check."""
    original = log_paths(stored)[0]
    copy = tmp_path / original.name
    text = original.read_text(encoding="utf-8")
    marker = '"move": "N"'
    if marker not in text:
        marker = next(f'"move": "{d}"' for d in "NESW" if f'"move": "{d}"' in text)
    swapped = "S" if '"S"' not in marker else "N"
    copy.write_text(text.replace(marker, f'"move": "{swapped}"', 1), encoding="utf-8")
    assert verify_records(load_log(copy).records).verdict is Verdict.TAMPERED


def test_the_stored_result_names_this_group(stored) -> None:
    """A log that verifies against somebody else's match is not our evidence. The result
    read back off disk has to name us."""
    result = next(body for name, body in stored.artifacts.items()
                  if name.startswith("result_"))
    assert any(entry["group_id"] == OUR_GROUP for entry in result["groups"])
