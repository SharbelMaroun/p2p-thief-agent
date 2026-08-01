"""The five orchestrator subsystem ports (`M5-001a`).

Book chapter 9 names five subsystems behind the Orchestrator: the MCP Connector, the
Decision Module, the Log Manager, the Deadline Tracker, and the Watchdog. Each is
expressed here as a narrow **port** — the smallest interface the gateway depends on — so
the gateway couples to behaviour, not to a concrete class, and any conforming
implementation (including a test double) slots in. The MCP Connector's port is
`peer.transport.PeerTransport`, reused here rather than restated.

Ports live in the orchestration layer, not inside any subsystem, so declaring them does
not create a subsystem-to-subsystem import (`M5-001b`).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from p2p_thief_agent.peer.transport import PeerTransport

__all__ = ["DeadlineTracker", "DecisionModule", "LogPort", "PeerTransport", "WatchdogPort"]


@runtime_checkable
class DecisionModule(Protocol):
    """Decide one turn from the opponent's last message (returns the message + seal)."""

    def decide(self, incoming: dict | None, step: int) -> tuple[dict, dict]: ...


@runtime_checkable
class LogPort(Protocol):
    """The append-only log the gateway drives on each phase transition."""

    def record_transition(self, phase: object) -> object: ...


@runtime_checkable
class DeadlineTracker(Protocol):
    """Opens one request's deadline from the agreed match limits."""

    def deadline(self, now: float) -> object: ...


@runtime_checkable
class WatchdogPort(Protocol):
    """Receives a heartbeat as the loop makes progress, and reports liveness."""

    def beat(self, now: float) -> None: ...

    def check(self, now: float) -> object: ...
