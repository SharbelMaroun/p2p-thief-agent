"""The negotiated serve path: projection, identity, and the live handshake (`M5-014f`).

Found by the first two-process rehearsal: the CLI's match path played unnegotiated,
which composes with nothing. These tests pin the seam that closed that gap.
"""

import queue

import pytest

from p2p_thief_agent.adapters.negotiated import (
    NegotiatedServeError,
    load_negotiation_inputs,
    negotiated_threshold,
)
from p2p_thief_agent.protocol.handshake import Handshake
from p2p_thief_agent.protocol.terms_projection import TermsProjectionError, terms_from_shared_config
from p2p_thief_agent.shared.private_config import PrivateConfigError, identity_from_private

SHARED = {
    "board_and_agents": {"grid_size": 7, "thief_start": [3, 3], "cop_start": [0, 0],
                         "axis_origin_corner": "top-left", "axis_start_index": 0},
    "world": {"map_area": "New York", "hint_max_words": 15},
    "movement_and_barriers": {"max_barriers": 14, "max_moves": 35},
    "pheromones": {"pheromone_center_intensity": 0.9, "pheromone_decay": 0.10,
                   "pheromone_grid_size": 5},
    "network_and_league": {"num_games": 6, "response_timeout_sec": 5},
}

PRIVATE = {
    "game": {"group_id": "g-thief", "group_name": "G Thief", "members": ["a", "b"],
             "repos": {"cop": "https://x/c", "thief": "https://x/t"}},
    "llm": {"model": "zero-token"},
    "hardware": {"cpu_freq_mhz": 3600, "ram_gb": 16, "gpu_model": "none"},
}


def identity():
    return identity_from_private(PRIVATE, "http://127.0.0.1:8801/mcp", "http://127.0.0.1:8802/mcp")


def test_the_projection_is_the_reference_roster() -> None:
    terms = terms_from_shared_config(SHARED)
    assert terms == {
        "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.10,
        "emit_intensity": 0.9, "max_steps": 35, "barriers_max": 14,
        "setting": "New York", "hint_max_words": 15, "axis_origin_corner": "top-left",
        "axis_start_index": 0, "thief_start": [3, 3], "cop_start": [0, 0],
        "num_games": 6,
    }


def test_a_missing_section_is_named_not_defaulted() -> None:
    broken = {**SHARED, "pheromones": {}}
    with pytest.raises(TermsProjectionError, match="pheromones.pheromone_grid_size"):
        terms_from_shared_config(broken)


def test_the_identity_carries_every_mandated_member() -> None:
    block = identity()
    assert set(block) == {"group_id", "group_name", "members", "repos",
                          "mcp_servers", "llm_model", "spec"}
    assert block["mcp_servers"] == {"thief": "http://127.0.0.1:8801/mcp",
                                    "cop": "http://127.0.0.1:8802/mcp"}


def test_a_short_identity_is_refused_by_name() -> None:
    private = {**PRIVATE, "llm": {"model": ""}}
    with pytest.raises(PrivateConfigError, match="llm_model"):
        identity_from_private(private, "http://a/mcp", "http://b/mcp")


def test_game_without_private_refuses_to_negotiate() -> None:
    with pytest.raises(NegotiatedServeError, match="--private"):
        load_negotiation_inputs("game.json", None, "http://a/mcp", "http://b/mcp")


class _Pair:
    """An in-memory opposite peer: acks our offer and queues its own signed one."""

    def __init__(self, terms, respond=True):
        self.inboxes = type("Boxes", (), {"agreements": queue.Queue()})()
        if respond:
            other = Handshake(terms=dict(terms), identity={
                "group_id": "g-cop", "group_name": "G Cop", "members": ["c"],
                "repos": {"cop": "https://x/c", "thief": "https://x/t"},
                "mcp_servers": {"cop": "http://b/mcp"}, "llm_model": "zero-token",
                "spec": {"ram_gb": 16},
            })
            self.inboxes.agreements.put(other.signed())

    def negotiate(self, _offer):
        return {"ok": True}


def test_the_live_handshake_agrees_and_returns_the_horizon() -> None:
    terms = terms_from_shared_config(SHARED)
    pair = _Pair(terms)
    threshold = negotiated_threshold(
        client=pair, inboxes=pair.inboxes, game_config=SHARED, identity=identity(),
        fallback_timeout=1.0, sleep=lambda _s: None,
    )
    assert threshold == 35


def test_a_differing_offer_is_refused_with_the_term_named() -> None:
    other_terms = {**terms_from_shared_config(SHARED), "max_steps": 60}
    pair = _Pair(other_terms)
    with pytest.raises(NegotiatedServeError, match="max_steps"):
        negotiated_threshold(
            client=pair, inboxes=pair.inboxes, game_config=SHARED, identity=identity(),
            fallback_timeout=1.0, sleep=lambda _s: None,
        )


def test_a_silent_opponent_is_a_bounded_refusal_not_a_hang() -> None:
    pair = _Pair(terms_from_shared_config(SHARED), respond=False)
    with pytest.raises(NegotiatedServeError, match="refused before play"):
        negotiated_threshold(
            client=pair, inboxes=pair.inboxes,
            game_config={**SHARED, "network_and_league": {"num_games": 6,
                                                          "response_timeout_sec": 0.2}},
            identity=identity(), fallback_timeout=0.2, sleep=lambda _s: None,
        )
