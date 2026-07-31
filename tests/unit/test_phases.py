"""`M5-007a`: the declared turn phase machine, and everything it refuses.

Rules 4 and 5 make the table the authority, so most of these tests assert what is
**not** allowed. A machine that accepted everything would pass a happy-path test and
still deadlock the first time a peer went out of order.
"""

import pytest

from p2p_thief_agent.orchestration.phases import (
    TRANSITIONS,
    TURN_CYCLE,
    Phase,
    PhaseError,
    PhaseMachine,
)

LEGAL = {(src, dst) for src, targets in TRANSITIONS.items() for dst in targets}
ALL_PAIRS = {(src, dst) for src in Phase for dst in Phase}
ORDER = {"key": lambda pair: (pair[0].value, pair[1].value)}


def test_the_table_matches_the_specification_listing() -> None:
    """A silent edit here would change a mandatory rule."""
    assert {
        Phase.WAITING_FOR_OPPONENT: frozenset({Phase.COMPUTING_MOVE}),
        Phase.COMPUTING_MOVE: frozenset({Phase.COMMITTING, Phase.TECHNICAL_LOSS}),
        Phase.COMMITTING: frozenset({Phase.AWAITING_REVEAL}),
        Phase.AWAITING_REVEAL: frozenset({Phase.VERIFYING, Phase.TECHNICAL_LOSS}),
        Phase.VERIFYING: frozenset({Phase.WAITING_FOR_OPPONENT}),
        Phase.TECHNICAL_LOSS: frozenset(),
    } == TRANSITIONS


def test_every_phase_has_a_declared_row() -> None:
    """A phase missing a row would raise KeyError instead of PhaseError."""
    assert set(TRANSITIONS) == set(Phase)


@pytest.mark.parametrize(("src", "dst"), sorted(LEGAL, **ORDER))
def test_every_declared_transition_is_accepted(src: Phase, dst: Phase) -> None:
    assert PhaseMachine(src).to(dst) is dst


@pytest.mark.parametrize(("src", "dst"), sorted(ALL_PAIRS - LEGAL, **ORDER))
def test_every_undeclared_transition_is_refused(src: Phase, dst: Phase) -> None:
    """`AE-005`: the refusal is the feature, and it names what it refused."""
    with pytest.raises(PhaseError, match="illegal transition"):
        PhaseMachine(src).to(dst)


def test_one_full_turn_walks_the_cycle_and_returns_to_waiting() -> None:
    machine = PhaseMachine()
    assert machine.complete_turn() == TURN_CYCLE
    assert machine.current is Phase.WAITING_FOR_OPPONENT


def test_turns_can_run_back_to_back() -> None:
    """Thirty-five per sub-game, so the cycle must be re-enterable."""
    machine = PhaseMachine()
    for _ in range(3):
        machine.complete_turn()
    assert machine.history.count(Phase.COMMITTING) == 3


def test_history_records_every_phase_in_order() -> None:
    machine = PhaseMachine()
    machine.complete_turn()
    assert machine.history == (Phase.WAITING_FOR_OPPONENT, *TURN_CYCLE)


def test_technical_loss_is_terminal() -> None:
    machine = PhaseMachine(Phase.AWAITING_REVEAL)
    assert machine.fail() is Phase.TECHNICAL_LOSS
    assert machine.is_terminal
    with pytest.raises(PhaseError, match="terminal"):
        machine.to(Phase.WAITING_FOR_OPPONENT)


@pytest.mark.parametrize("src", [Phase.COMPUTING_MOVE, Phase.AWAITING_REVEAL])
def test_a_mid_turn_fault_has_a_defined_exit(src: Phase) -> None:
    """`AE-007`: a disconnect must terminate, never deadlock."""
    assert PhaseMachine(src).fail() is Phase.TECHNICAL_LOSS


@pytest.mark.parametrize("src", [Phase.WAITING_FOR_OPPONENT, Phase.COMMITTING, Phase.VERIFYING])
def test_a_technical_loss_cannot_be_declared_from_an_undeclared_phase(src: Phase) -> None:
    """Abandoning an uncommitted turn is not in the table, so it is refused."""
    with pytest.raises(PhaseError, match="illegal transition"):
        PhaseMachine(src).fail()


@pytest.mark.parametrize("bad", ["COMMITTING", None, 3])
def test_a_non_phase_target_is_refused(bad: object) -> None:
    with pytest.raises(PhaseError, match="must be a Phase"):
        PhaseMachine().to(bad)


@pytest.mark.parametrize("bad", ["WAITING_FOR_OPPONENT", None])
def test_a_non_phase_start_is_refused(bad: object) -> None:
    with pytest.raises(PhaseError, match="start must be a Phase"):
        PhaseMachine(bad)
