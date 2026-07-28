"""Public SDK exports.

All Thief business behavior is reached through this boundary (`PS-007`). The M2 domain
types and functions are re-exported here so adapters never import internal modules
directly or duplicate business logic.
"""

from p2p_thief_agent import domain
from p2p_thief_agent.domain import (
    DEFAULT_BARRIER_QUOTA,
    Action,
    BarrierField,
    Board,
    CaptureReason,
    Coordinate,
    DomainError,
    OriginCorner,
    cardinal_moves,
    evaluate_capture,
    is_captured,
    is_orthogonal_step,
    is_trapped,
    legal_actions,
    resolve_move,
    validate_barrier_placement,
)
from p2p_thief_agent.sdk.api import ThiefSdk

__all__ = [
    "DEFAULT_BARRIER_QUOTA",
    "Action",
    "BarrierField",
    "Board",
    "CaptureReason",
    "Coordinate",
    "DomainError",
    "OriginCorner",
    "ThiefSdk",
    "cardinal_moves",
    "domain",
    "evaluate_capture",
    "is_captured",
    "is_orthogonal_step",
    "is_trapped",
    "legal_actions",
    "resolve_move",
    "validate_barrier_placement",
]
