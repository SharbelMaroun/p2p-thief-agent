"""Public SDK exports.

All Thief business behavior is reached through this boundary (`PS-007`). The M2 domain
types and functions and the deterministic baseline strategy are re-exported here so
adapters never import internal modules directly or duplicate business logic.
"""

from p2p_thief_agent import domain, strategy
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
from p2p_thief_agent.strategy import (
    choose_action,
    edge_contacts,
    is_dead_end,
    manhattan_distance,
    min_threat_distance,
    mobility,
    onward_reach,
    rank_actions,
)

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
    "choose_action",
    "domain",
    "edge_contacts",
    "evaluate_capture",
    "is_captured",
    "is_dead_end",
    "is_orthogonal_step",
    "is_trapped",
    "legal_actions",
    "manhattan_distance",
    "min_threat_distance",
    "mobility",
    "onward_reach",
    "rank_actions",
    "resolve_move",
    "strategy",
    "validate_barrier_placement",
]
