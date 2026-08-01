"""Thief orchestration: the declared phase machine, the turn loop, and a sub-game.

Transport stays absent by construction — every module here takes a transport and a
receive callable and imports no FastMCP symbol, so a whole sub-game runs without a
socket and the same code runs over one.
"""

from p2p_thief_agent.orchestration.gateway import Gateway
from p2p_thief_agent.orchestration.phases import (
    TRANSITIONS,
    TURN_CYCLE,
    Phase,
    PhaseError,
    PhaseMachine,
)
from p2p_thief_agent.orchestration.ports import (
    DeadlineTracker,
    DecisionModule,
    LogPort,
    PeerTransport,
    WatchdogPort,
)
from p2p_thief_agent.orchestration.sub_game import (
    AnswerClaim,
    SubGameOutcome,
    run_sub_game_over_wire,
)
from p2p_thief_agent.orchestration.turn_loop import (
    Decide,
    OnTransition,
    Receive,
    TurnLoopError,
    TurnRecord,
    is_sealed_once,
    run_turn,
    sealed_steps,
)

__all__ = [
    "TRANSITIONS",
    "TURN_CYCLE",
    "AnswerClaim",
    "DeadlineTracker",
    "Decide",
    "DecisionModule",
    "Gateway",
    "LogPort",
    "OnTransition",
    "PeerTransport",
    "Phase",
    "PhaseError",
    "PhaseMachine",
    "Receive",
    "SubGameOutcome",
    "TurnLoopError",
    "TurnRecord",
    "WatchdogPort",
    "is_sealed_once",
    "run_sub_game_over_wire",
    "run_turn",
    "sealed_steps",
]
