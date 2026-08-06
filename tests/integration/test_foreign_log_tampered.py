"""`M8-012b`: the detection path is not self-only.

Verifying our own honest log proves the reader agrees with the writer. Catching a forgery
in a log **we did not write** is what rule 36's mutual audit is actually for, and it is
what stands between an opponent rewriting a losing move and a clean `Verified OK`.

Each test is a different shape of lie, chosen because each defeats a cheaper check than
the last: a rewritten payload defeats eyeballing, a swapped nonce defeats field-shape
validation, and a rewritten *visible* field defeats the digest check itself.
"""

from __future__ import annotations

from pathlib import Path

from p2p_thief_agent.replay import Replay, Verdict, load_log
from tests.integration.foreign_log_writer import foreign_writer, write_foreign_log


def _replay(tmp_path: Path, document: dict) -> Replay:
    return Replay(load_log(write_foreign_log(tmp_path, document)))


def test_a_forged_foreign_log_is_detected(tmp_path: Path) -> None:
    """An opponent rewriting their own move after the fact — the attack the whole
    commit-reveal scheme exists to stop."""
    document = foreign_writer(5)
    document["records"][3]["payload"]["move"] = "W"  # sealed as "N"
    document["records"][3]["move"] = "W"

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.TAMPERED
    assert replay.go_to_first_divergence() == 3
    assert replay.record["step"] == 4


def test_a_foreign_log_with_a_swapped_nonce_is_detected(tmp_path: Path) -> None:
    """Swapping two valid nonces keeps every field well-formed and every value real — a
    shape check, or an "is this 32 hex characters" check, would pass it."""
    document = foreign_writer(4)
    records = document["records"]
    records[0]["nonce"], records[1]["nonce"] = records[1]["nonce"], records[0]["nonce"]
    assert _replay(tmp_path, document).stamp is Verdict.TAMPERED


def test_rewriting_only_the_displayed_move_is_detected(tmp_path: Path) -> None:
    """Leave the sealed payload alone so every digest matches, and change only what the
    board shows. Without the visible-field check this replays a fictional game under a
    green stamp. `:1691` requires the viewer to re-encode "the Nonce and the move
    **appearing in the log**"."""
    document = foreign_writer(4)
    record = document["records"][2]
    assert record["move"] == record["payload"]["move"], "honest before we touch it"
    record["move"] = "X"

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.TAMPERED
    assert "contradicts the sealed payload" in replay.banner


def test_stripping_a_single_nonce_is_detected_rather_than_read_as_in_play(
    tmp_path: Path,
) -> None:
    """All nonces absent is an honest in-play log. One absent is a log revealed and then
    interfered with, and it must reach a verdict rather than a refusal."""
    document = foreign_writer(4)
    del document["records"][1]["nonce"]

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.TAMPERED
    assert "nonce" in replay.verdict.checks[1].reason


def test_a_forgery_leaves_the_other_records_verifiable(tmp_path: Path) -> None:
    """The match is void either way, but the auditor's next question is *which step* — and
    a verifier that gave up at the first failure could not answer it."""
    document = foreign_writer(6)
    document["records"][2]["commit"] = "0" * 64

    checks = _replay(tmp_path, document).verdict.checks
    assert [check.ok for check in checks] == [True, True, False, True, True, True]


# --- structural forgeries: reported, not bannered (M8-008d) ------------------------------


def test_an_appended_record_is_caught_by_the_visible_field_check(tmp_path: Path) -> None:
    """Inventing a step nobody played, with a commit copied from a real record. The copied
    payload still seals step 1, so the visible `step` gives it away — a digest check alone
    passes this."""
    document = foreign_writer(3)
    document["records"].append({**document["records"][0], "step": 4})
    assert _replay(tmp_path, document).stamp is Verdict.TAMPERED


def test_a_reordered_foreign_log_verifies_but_is_reported(tmp_path: Path) -> None:
    """The deliberate asymmetry. Neither the book nor the reference requires ordering, so
    red-bannering an honest opponent over it would be a false accusation with no appeal
    (`:1769`) — and rule 35 scores zero for *both* teams on a contradicting report. So the
    banner stays green and the anomaly is reported for settlement to weigh."""
    document = foreign_writer(5)
    document["records"] = [document["records"][i] for i in (0, 3, 1, 4, 2)]

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.VERIFIED_OK
    assert not replay.sequence.contiguous
    assert any(f.kind == "out-of-order" for f in replay.sequence.findings)


def test_a_foreign_log_with_a_deleted_step_is_reported_as_a_gap(tmp_path: Path) -> None:
    """p.39/102 requires each side to present its "full log"; a gap makes the two reports
    contradictory, which is rule 35's question and not the digest's."""
    document = foreign_writer(6)
    del document["records"][2]

    replay = _replay(tmp_path, document)
    assert replay.stamp is Verdict.VERIFIED_OK
    finding = next(f for f in replay.sequence.findings if f.kind == "gap")
    assert finding.rule == "AE-35" and "[3]" in finding.detail
