"""`M7-018d`: leaving before the opponent's audit turns a won game into 0/0.

Played live against `uoh-ay26` on 2026-08-11: we survived 35 steps, wrote the log and
exited. Their `submit_audit` met a 502 and they recorded a technical loss, so their
artifact said `technical_loss` while ours said `survival` — rule 35 scores that 0/0 for
both. Every test here drives the window to both outcomes, because a wait that can only
succeed proves nothing.
"""

from __future__ import annotations

from p2p_thief_agent.adapters.post_match import (
    DEFAULT_AUDIT_WINDOW,
    audit_window_seconds,
    await_opponent_audit,
    log_context,
)


class _Clock:
    """A clock the test advances, so no test ever sleeps in real time."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += max(seconds, 0.01)


def test_an_audit_that_arrives_is_waited_for() -> None:
    """The whole point: the process must still be listening when their audit lands."""
    clock = _Clock()
    arrivals = {"n": 0}

    def drain() -> None:
        # Arrives on the third poll — after the match, as a real opponent's would.
        if clock.now > 1.0:
            arrivals["n"] = 1

    assert await_opponent_audit(
        drain=drain, audits_seen=lambda: arrivals["n"],
        clock=clock, sleep=clock.sleep, timeout=30.0) is True


def test_a_silent_opponent_closes_the_window_rather_than_hanging() -> None:
    """Rule 6: their silence must not become our freeze. Expiry is normal, not an error."""
    clock = _Clock()
    assert await_opponent_audit(
        drain=lambda: None, audits_seen=lambda: 0,
        clock=clock, sleep=clock.sleep, timeout=5.0) is False
    assert clock.now >= 5.0


def test_a_zero_window_still_reports_an_audit_already_in_hand() -> None:
    """A disabled window must not discard an audit that already arrived."""
    assert await_opponent_audit(
        drain=lambda: None, audits_seen=lambda: 1,
        clock=_Clock(), sleep=lambda _s: None, timeout=0.0) is True
    assert await_opponent_audit(
        drain=lambda: None, audits_seen=lambda: 0,
        clock=_Clock(), sleep=lambda _s: None, timeout=0.0) is False


def test_the_window_comes_from_the_private_toml() -> None:
    assert audit_window_seconds({"network": {"audit_send_timeout_seconds": 90}}) == 90.0
    assert audit_window_seconds({"network": {}}) == DEFAULT_AUDIT_WINDOW
    assert audit_window_seconds({}) == DEFAULT_AUDIT_WINDOW
    assert audit_window_seconds(None) == DEFAULT_AUDIT_WINDOW


def test_a_boolean_is_not_a_timeout() -> None:
    """`True` is an `int` in Python, and a one-second audit window is a silent 0/0."""
    assert audit_window_seconds({"network": {"audit_send_timeout_seconds": True}}) == \
        DEFAULT_AUDIT_WINDOW


def test_confirmed_reports_the_audit_rather_than_asserting_it() -> None:
    """It was the literal `True` before, which claimed an agreement that never happened."""
    common = {"sha": "ab" * 32, "sub_game": 1, "identity": {"group_id": "sharNamr"},
              "opponent_group_id": "uoh-ay26", "started_at": "2026-08-11T21:03:01+00:00"}
    assert log_context(**common, confirmed=True)["confirmed"] is True
    assert log_context(**common, confirmed=False)["confirmed"] is False


def test_the_context_identifiers_derive_from_the_config_hash() -> None:
    sha = "5a7b4a6e58be447982bcc5ca1b3b9ad160190e9127edb13b7c7d4e9e171e9f01"
    context = log_context(
        sha=sha, sub_game=2, identity={"group_id": "sharNamr"},
        opponent_group_id="uoh-ay26", started_at="t", confirmed=False)
    assert context["game_id"] == "game-5a7b4a6e58be"
    assert context["game_uid"] == sha[:32]
    assert context["config_sha256"] == sha
