"""The baseline strategy must be reachable through the public SDK boundary (PS-007)."""

import inspect

from p2p_thief_agent import sdk
from p2p_thief_agent.strategy import baseline, metrics

STRATEGY_EXPORTS = (
    "choose_action",
    "edge_contacts",
    "is_dead_end",
    "manhattan_distance",
    "min_threat_distance",
    "mobility",
    "onward_reach",
    "rank_actions",
)


def test_sdk_exports_every_strategy_symbol():
    for name in STRATEGY_EXPORTS:
        assert name in sdk.__all__
        assert hasattr(sdk, name)


def test_sdk_exposes_the_strategy_namespace():
    assert sdk.strategy.choose_action is baseline.choose_action


def test_sdk_symbols_are_the_strategy_implementations():
    assert sdk.choose_action is baseline.choose_action
    assert sdk.rank_actions is baseline.rank_actions
    assert sdk.is_dead_end is baseline.is_dead_end
    assert sdk.mobility is metrics.mobility


def test_sdk_all_has_no_duplicates_and_resolves():
    assert len(sdk.__all__) == len(set(sdk.__all__))
    for name in sdk.__all__:
        assert hasattr(sdk, name)


def test_choosing_an_action_through_the_sdk_returns_a_legal_action():
    board = sdk.Board(size=7)
    here = sdk.Coordinate(3, 3)
    chosen = sdk.choose_action(board, here, [sdk.Coordinate(0, 0)])
    assert chosen in sdk.legal_actions(board, here)


def test_strategy_modules_perform_no_networking_or_external_calls():
    for module in (baseline, metrics):
        source = inspect.getsource(module)
        for forbidden in ("import socket", "import requests", "urllib", "httpx", "subprocess"):
            assert forbidden not in source


def test_strategy_modules_do_not_import_protocol_or_orchestration_layers():
    for module in (baseline, metrics):
        source = inspect.getsource(module)
        assert "p2p_thief_agent.protocol" not in source
        assert "p2p_thief_agent.orchestration" not in source
