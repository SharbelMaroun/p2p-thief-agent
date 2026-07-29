"""Thief-local state, scoring, and baseline integration (M3).

Every symbol here is contract-independent and holds no Cop-private truth: the state
models only the Thief's own position, step count, disclosed-barrier knowledge, and an
immutable history; scoring encodes the official FIXED Appendix F Table 17 points; and
the policy layer binds the deterministic baseline to that state. Nothing here performs
networking, reads a Cop module, or depends on a shared-contract byte.
"""

from p2p_thief_agent.state.known_barriers import KnownBarriers
from p2p_thief_agent.state.local_state import ThiefLocalState, ThiefSnapshot
from p2p_thief_agent.state.policy import (
    choose_local_action,
    local_outcome,
    rank_local_actions,
    step_with_baseline,
)
from p2p_thief_agent.state.scoring import (
    CAPTURE_COP,
    CAPTURE_THIEF,
    DEFAULT_SURVIVAL_THRESHOLD,
    SURVIVAL_COP,
    SURVIVAL_THIEF,
    TECHNICAL_LOSS_SCORE,
    TIE_SCORE,
    Outcome,
    resolve_outcome,
    thief_score,
)

__all__ = [
    "CAPTURE_COP",
    "CAPTURE_THIEF",
    "DEFAULT_SURVIVAL_THRESHOLD",
    "KnownBarriers",
    "Outcome",
    "SURVIVAL_COP",
    "SURVIVAL_THIEF",
    "TECHNICAL_LOSS_SCORE",
    "TIE_SCORE",
    "ThiefLocalState",
    "ThiefSnapshot",
    "choose_local_action",
    "local_outcome",
    "rank_local_actions",
    "resolve_outcome",
    "step_with_baseline",
    "thief_score",
]
