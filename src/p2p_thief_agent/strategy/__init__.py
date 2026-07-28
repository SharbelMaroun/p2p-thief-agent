"""Deterministic Thief policies.

Every symbol here is pure and contract-independent: it uses only the public domain
APIs, takes all board, threat, and barrier inputs explicitly, holds no Cop-private
truth, performs no networking or external call, and defines no new game rule.
"""

from p2p_thief_agent.strategy.baseline import choose_action, is_dead_end, rank_actions
from p2p_thief_agent.strategy.metrics import (
    edge_contacts,
    manhattan_distance,
    min_threat_distance,
    mobility,
    onward_reach,
)

__all__ = [
    "choose_action",
    "edge_contacts",
    "is_dead_end",
    "manhattan_distance",
    "min_threat_distance",
    "mobility",
    "onward_reach",
    "rank_actions",
]
