"""The pre-game offer wait honours the connect budget, not the in-game timer.

Second amireman smoke, 2026-08-13: their sub-game-2 negotiate landed on our game-1
agent's audit window and was gone; our Thief then waited only ``response_timeout_sec``
(30) for a fresh offer and quit the series as "refused before play". The offer wait is
patience for an opponent who does not exist yet — the connect budget's job — while the
30-second timer governs requests inside a running game.
"""

import contextlib

from p2p_thief_agent.adapters import negotiated

CONFIG = {
    "network_and_league": {"response_timeout_sec": 30},
    "movement_and_barriers": {"max_moves": 35, "survival_threshold": 35,
                              "max_barriers": 14, "move_set": ["N", "S", "E", "W", "STAY"]},
}


def test_the_offer_wait_uses_the_connect_budget_as_floor(monkeypatch) -> None:
    seen = {}

    def spy(**kwargs):
        seen["timeout"] = kwargs["timeout"]
        raise negotiated.NegotiationError("stop here")

    monkeypatch.setattr(negotiated, "negotiate_for_serve", spy)
    monkeypatch.setattr(negotiated, "terms_from_shared_config", lambda _c: {})
    with contextlib.suppress(negotiated.NegotiatedServeError):
        negotiated.negotiated_agreement(
            client=object(), inboxes=object(), game_config=CONFIG,
            identity={"group_id": "sharNamr"}, fallback_timeout=600.0, sleep=lambda _s: None,
        )
    assert seen["timeout"] == 600.0


def test_a_longer_response_timeout_still_wins(monkeypatch) -> None:
    """max(), not replacement: a shared file demanding more patience keeps it."""
    seen = {}

    def spy(**kwargs):
        seen["timeout"] = kwargs["timeout"]
        raise negotiated.NegotiationError("stop here")

    monkeypatch.setattr(negotiated, "negotiate_for_serve", spy)
    monkeypatch.setattr(negotiated, "terms_from_shared_config", lambda _c: {})
    generous = {"network_and_league": {"response_timeout_sec": 900}}
    with contextlib.suppress(negotiated.NegotiatedServeError):
        negotiated.negotiated_agreement(
            client=object(), inboxes=object(), game_config=generous,
            identity={"group_id": "sharNamr"}, fallback_timeout=600.0, sleep=lambda _s: None,
        )
    assert seen["timeout"] == 900.0
