"""The orchestrator gateway (`M5-001`).

Book chapter 9: a single Orchestrator splits into five subsystems and *all* communication
between them passes through it. This gateway is that composition root — it holds one port
of each kind (`M5-001a`) and wires them together. Two disciplines make it a gateway
rather than a god-object:

- **It decides nothing** (`M5-001c`). The move always comes from the Decision Module;
  `on_transition` merely fans a phase change out to the Log Manager and the Watchdog.
  There is no game logic here to find.
- **The subsystems never import each other** (`M5-001b`). They meet only here — the Log
  Manager and the Watchdog, for instance, both react to a transition without either
  knowing the other exists, because the gateway is what calls both.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from p2p_thief_agent.orchestration.phases import Phase, PhaseMachine
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
from p2p_thief_agent.orchestration.turn_loop import Receive


@dataclass(frozen=True, slots=True)
class Gateway:
    """Coordinates the five subsystems. It coordinates; it does not decide."""

    mcp: PeerTransport
    decision: DecisionModule
    log: LogPort
    deadlines: DeadlineTracker
    watchdog: WatchdogPort
    clock: Callable[[], float]

    def on_transition(self, phase: Phase) -> None:
        """Fan a phase transition out to the subsystems that track progress.

        The Log Manager records it and the Watchdog gets a heartbeat — proof the loop is
        still alive. Neither subsystem imports the other; they meet only through here.
        """
        self.log.record_transition(phase)
        self.watchdog.beat(self.clock())

    def next_deadline(self, now: float) -> object:
        """Open one request's deadline from the agreed limits (for the send path)."""
        return self.deadlines.deadline(now)

    def play_sub_game(
        self,
        *,
        receive: Receive,
        answer_claim: AnswerClaim,
        survival_threshold: int,
        records: list[dict] | None = None,
    ) -> SubGameOutcome:
        """Coordinate one sub-game, delegating every move to the Decision Module.

        The gateway wires the MCP Connector, the Decision Module, and the log/watchdog
        fan-out into the turn loop; `decide` is the Decision Module's, so no game logic
        lives here (`M5-001c`).
        """
        return run_sub_game_over_wire(
            machine=PhaseMachine(),
            transport=self.mcp,
            receive=receive,
            decide=self.decision.decide,
            answer_claim=answer_claim,
            survival_threshold=survival_threshold,
            records=records,
            on_transition=self.on_transition,
        )
