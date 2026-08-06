"""`M8-008` / `M8-008a`: stepping through a replay, and never trusting a stale verdict.

`:1689` asks for navigation "forward and backward in time using playback controls";
`DEV-SPEC.md:426` restates it. `M8-008a` adds the condition that matters: the verdict is
recomputed on every navigation, never cached from load time. The test that proves it is
`test_tampering_between_two_navigations_flips_the_banner`; the rest are its preconditions.
"""

from __future__ import annotations

import hashlib
import json

from p2p_thief_agent.replay import Replay, Verdict, parse_log

NONCE = "d4" * 16


def _record(step: int) -> dict:
    payload = {"step": step, "move": "E"}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return {"step": step, "sender": "thief", "move": "E", "payload": payload, "nonce": NONCE,
            "commit": hashlib.sha256(f"{canonical}|{NONCE}".encode()).hexdigest()}


def _replay(count: int = 5) -> Replay:
    return Replay(parse_log({"game_id": "nav", "records": [_record(n) for n in range(1, count + 1)]}))


# --- M8-008: the controls ---------------------------------------------------------------


def test_step_forward_and_back_walk_the_log() -> None:
    replay = _replay()
    assert replay.position == 0
    assert replay.step_forward() == 1
    assert replay.step_forward() == 2
    assert replay.step_back() == 1


def test_the_cursor_clamps_at_both_ends_instead_of_raising() -> None:
    """A `Next` button that throws at the last record crashes during the demonstration it
    exists to produce — and that demonstration is the submission evidence."""
    replay = _replay(3)
    for _ in range(10):
        replay.step_forward()
    assert replay.position == 2
    for _ in range(10):
        replay.step_back()
    assert replay.position == 0


def test_go_to_jumps_by_index_and_go_to_step_jumps_by_the_logs_own_numbering() -> None:
    replay = _replay(6)
    assert replay.go_to(4) == 4
    assert replay.go_to_step(2) == 1, "step 2 is the record at index 1"
    assert replay.record["step"] == 2


def test_go_to_an_unknown_step_leaves_the_cursor_where_it_was() -> None:
    """A log whose numbering we do not recognise is exactly the log we still want open."""
    replay = _replay(3)
    replay.go_to(1)
    assert replay.go_to_step(99) == 1


def test_restart_returns_to_the_first_record() -> None:
    replay = _replay()
    replay.go_to(3)
    assert replay.restart() == 0


def test_go_to_first_divergence_lands_on_the_forged_record() -> None:
    """The one navigation an auditor performs — `:1769` has already decided the match, so
    the remaining question is *which step*."""
    replay = _replay(6)
    replay.log.records[3]["payload"] = {"step": 4, "move": "W"}  # type: ignore[index]
    assert replay.go_to_first_divergence() == 3
    assert replay.record["step"] == 4


def test_go_to_first_divergence_returns_none_on_a_clean_log() -> None:
    assert _replay().go_to_first_divergence() is None


# --- M8-008a: the verdict is recomputed, not remembered ---------------------------------


def test_tampering_between_two_navigations_flips_the_banner() -> None:
    """**The test this module exists for.** A verdict computed at load and painted forever
    is a claim about the past tense; the `Verified OK` stamp is submission evidence, so it
    must track the bytes it describes at the moment it is read. No reload happens here."""
    replay = _replay(4)
    assert replay.stamp is Verdict.VERIFIED_OK

    replay.step_forward()
    replay.log.records[2]["commit"] = "0" * 64  # type: ignore[index]

    assert replay.stamp is Verdict.TAMPERED
    assert "step 3" in replay.banner


def test_repairing_a_log_flips_the_banner_back() -> None:
    """The other direction, which proves the flip above is recomputation rather than a
    latch that only ever trips one way."""
    replay = _replay(3)
    original = replay.log.records[1]["commit"]
    replay.log.records[1]["commit"] = "f" * 64  # type: ignore[index]
    assert replay.stamp is Verdict.TAMPERED

    replay.log.records[1]["commit"] = original  # type: ignore[index]
    assert replay.stamp is Verdict.VERIFIED_OK


def test_the_replay_object_stores_no_verdict_to_go_stale() -> None:
    """Belt and braces: the guarantee above is structural, so assert the structure."""
    assert set(vars(_replay())) == {"_log", "_position"}


def test_the_per_record_check_is_recomputed_too() -> None:
    """A cached per-record verdict would be the same bug one level down."""
    replay = _replay(3)
    replay.go_to(1)
    assert replay.check.ok
    replay.log.records[1]["nonce"] = "0" * 32  # type: ignore[index]
    assert not replay.check.ok


def test_the_sequence_report_is_recomputed_on_every_read_as_well() -> None:
    """The structural report is derived on the same terms as the verdict; caching it would
    let a shuffle introduced mid-session go unreported."""
    replay = _replay(4)
    assert replay.sequence.contiguous
    replay.log.records.reverse()  # type: ignore[attr-defined]
    assert not replay.sequence.contiguous


def test_navigation_does_not_change_the_verdict_on_an_honest_log() -> None:
    """Recomputing on every move must be *stable*: an auditor clicking through a clean log
    must not see the banner flicker, or the evidence means nothing."""
    replay = _replay(5)
    for position in (0, 1, 2, 3, 4, 3, 2, 1, 0):
        replay.go_to(position)
        assert replay.stamp is Verdict.VERIFIED_OK
