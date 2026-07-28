"""Verified Thief domain: coordinates, board, movement, barriers, and capture.

Every symbol here encodes only Appendix E/F CONFIRMED rules and takes explicit inputs.
The domain holds no Cop-private truth and depends on no shared-contract byte.
"""

from p2p_thief_agent.domain.barriers import (
    DEFAULT_BARRIER_QUOTA,
    BarrierField,
    validate_barrier_placement,
)
from p2p_thief_agent.domain.board import Board, OriginCorner, is_orthogonal_step
from p2p_thief_agent.domain.capture import (
    CaptureReason,
    evaluate_capture,
    is_captured,
    is_trapped,
)
from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError
from p2p_thief_agent.domain.movement import (
    cardinal_moves,
    legal_actions,
    resolve_move,
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
    "cardinal_moves",
    "evaluate_capture",
    "is_captured",
    "is_orthogonal_step",
    "is_trapped",
    "legal_actions",
    "resolve_move",
    "validate_barrier_placement",
]
