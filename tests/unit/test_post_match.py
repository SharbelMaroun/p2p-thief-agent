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


def test_it_lingers_after_the_audit_so_the_opponent_can_tear_down() -> None:
    """The teardown-race fix (2026-08-12): exiting the instant the audit lands leaves the
    opponent's client hitting a dead origin (502). We keep serving for the grace window and
    keep draining, so a late follow-up or duplicate is absorbed rather than refused."""
    clock = _Clock()
    arrivals = {"n": 0}
    drains_after_receipt = {"n": 0}
    received_at: dict[str, float] = {}

    def drain() -> None:
        if clock.now >= 1.0 and arrivals["n"] == 0:
            arrivals["n"] = 1
            received_at["t"] = clock.now
        if arrivals["n"]:
            drains_after_receipt["n"] += 1

    assert await_opponent_audit(
        drain=drain, audits_seen=lambda: arrivals["n"],
        clock=clock, sleep=clock.sleep, timeout=30.0, grace=12.0) is True
    # Returned only after lingering the full grace past receipt, still draining.
    assert clock.now >= received_at["t"] + 12.0
    assert drains_after_receipt["n"] > 1


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
              "opponent_group_id": "uoh-ay26", "started_at": "2026-08-11T21:03:01+00:00",
              "game_id": "G009", "game_uid": "7b1d942e-5a9c-6e0c-312a-761dd7dec131"}
    assert log_context(**common, confirmed=True)["confirmed"] is True
    assert log_context(**common, confirmed=False)["confirmed"] is False


def test_the_context_identifiers_are_supplied_not_derived_from_the_hash() -> None:
    """The regression: these used to be `game-<sha[:12]>` and `sha[:32]`.

    Appendix F table 20 names all four artifacts from `<game_id>`, and the book says that
    identifier is the agreed label rather than a config digest. The old derivation split
    the counted G009 series across two naming schemes -- this side wrote
    `log_game-5a7b4a6e58be_g01.json` while the companion wrote `config_G009_g02.json` --
    so the identifiers are now passed in and the config hash keeps its own field.
    """
    sha = "5a7b4a6e58be447982bcc5ca1b3b9ad160190e9127edb13b7c7d4e9e171e9f01"
    context = log_context(
        sha=sha, sub_game=2, identity={"group_id": "sharNamr"},
        opponent_group_id="uoh-ay26", started_at="t", confirmed=False,
        game_id="G009", game_uid="7b1d942e-5a9c-6e0c-312a-761dd7dec131")
    assert context["game_id"] == "G009"
    assert context["game_uid"] == "7b1d942e-5a9c-6e0c-312a-761dd7dec131"
    assert context["config_sha256"] == sha
    assert "game-" not in context["game_id"]
