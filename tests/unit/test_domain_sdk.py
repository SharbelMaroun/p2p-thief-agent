"""Tests that the M2 domain is reachable through the public SDK (PS-007)."""

from p2p_thief_agent import sdk
from p2p_thief_agent.sdk import (
    Action,
    BarrierField,
    Board,
    CaptureReason,
    Coordinate,
    evaluate_capture,
    legal_actions,
    resolve_move,
)


def test_domain_symbols_are_exported_by_sdk() -> None:
    """The SDK re-exports every public domain symbol."""
    for name in (
        "Action", "Board", "BarrierField", "CaptureReason", "Coordinate",
        "DomainError", "OriginCorner", "cardinal_moves", "evaluate_capture",
        "is_captured", "is_orthogonal_step", "is_trapped", "legal_actions",
        "resolve_move", "validate_barrier_placement", "DEFAULT_BARRIER_QUOTA",
    ):
        assert name in sdk.__all__
        assert hasattr(sdk, name)


def test_sdk_domain_namespace_is_available() -> None:
    """The whole domain module is reachable as sdk.domain."""
    assert sdk.domain.Coordinate(1, 2) == Coordinate(1, 2)


def test_end_to_end_move_then_capture_through_sdk() -> None:
    """A short scripted scenario runs entirely through SDK-exported symbols."""
    board = Board(size=7)
    thief = Coordinate(3, 3)

    moved = resolve_move(board, thief, Action.EAST)
    assert moved == Coordinate(3, 4)
    assert Action.STAY in legal_actions(board, moved)

    walls = frozenset(
        {Coordinate(2, 4), Coordinate(4, 4), Coordinate(3, 5), Coordinate(3, 3)}
    )
    barriers = BarrierField(walls, quota=4)
    assert evaluate_capture(board, moved, Coordinate(0, 0), barriers) is (
        CaptureReason.TRAPPED
    )
