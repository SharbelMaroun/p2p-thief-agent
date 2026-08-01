"""`M5-001`: the orchestrator gateway coordinates the five subsystems and decides nothing.

The gateway holds one port of each kind and wires them together. The move comes from the
Decision Module (a spy proves the gateway itself computes nothing), and a phase
transition fans out to both the Log Manager and the Watchdog through the single
`on_transition` seam — neither subsystem knowing the other exists.
"""

from p2p_thief_agent.orchestration.gateway import Gateway
from p2p_thief_agent.orchestration.phases import Phase
from p2p_thief_agent.services.deadlines import RetryPolicy
from p2p_thief_agent.state.scoring import Outcome
from tests.unit.test_turn_loop import Sink, decide


class SpyDecision:
    def __init__(self) -> None:
        self.calls = 0

    def decide(self, incoming: dict | None, step: int) -> tuple[dict, dict]:
        self.calls += 1
        return decide(incoming, step)


class SpyLog:
    def __init__(self) -> None:
        self.transitions: list[object] = []

    def record_transition(self, phase: object) -> object:
        self.transitions.append(phase)
        return phase


class SpyWatchdog:
    def __init__(self) -> None:
        self.beats: list[float] = []

    def beat(self, now: float) -> None:
        self.beats.append(now)

    def check(self, now: float) -> str:
        return "ALIVE"


class Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


def build() -> Gateway:
    return Gateway(
        mcp=Sink(), decision=SpyDecision(), log=SpyLog(),
        deadlines=RetryPolicy.from_match({}), watchdog=SpyWatchdog(), clock=Clock(),
    )


def test_the_gateway_holds_all_five_subsystem_ports() -> None:
    gw = build()
    assert gw.mcp and gw.decision and gw.log and gw.deadlines and gw.watchdog


def test_on_transition_fans_out_to_the_log_and_the_watchdog() -> None:
    gw = build()
    gw.on_transition(Phase.COMPUTING_MOVE)
    assert gw.log.transitions == [Phase.COMPUTING_MOVE]
    assert len(gw.watchdog.beats) == 1


def test_next_deadline_comes_from_the_deadline_tracker() -> None:
    gw = build()
    assert gw.next_deadline(100.0).expires == 130.0  # response_timeout default 30


def test_play_sub_game_delegates_the_move_to_the_decision_module() -> None:
    gw = build()
    result = gw.play_sub_game(
        receive=lambda: None, answer_claim=lambda _cell: False, survival_threshold=1,
    )
    assert result.outcome is Outcome.SURVIVAL and result.steps == 1
    assert gw.decision.calls == 1, "the gateway did not decide; the module did"
    assert Phase.COMPUTING_MOVE in gw.log.transitions and gw.watchdog.beats
