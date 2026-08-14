"""Wall awareness: the interceptor model, the one-wall trap, and the fail-safe (`M6-032`).

The waller grid measured the gap these exist for: a pursuer spending its Appendix-F
quota on seals converted 16 of 24 evasions, and every mover model was structurally
blind to it — the seal fires once the thief already stands in a two-exit corner, so
the refusal has to happen while the graph is still open.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.orchestration import thief_policy
from p2p_thief_agent.perception.field import blank_field, deposit
from p2p_thief_agent.perception.observation import encode_smell_grid
from p2p_thief_agent.strategy import adaptive_policy
from p2p_thief_agent.strategy.metrics import one_wall_trap, wall_pressure
from p2p_thief_agent.strategy.pursuer_models import PURSUERS, interceptor_step

BOARD = Board(size=7)
NONE_BLOCKED: frozenset[Coordinate] = frozenset()


def test_the_interceptor_closes_the_pinned_axis() -> None:
    """From the west edge against an east-edge bobber the summed race crosses the
    board — the strongest cheap mover a classmate can ship, so the planner must be
    able to assume it."""
    stepped = interceptor_step(BOARD, Coordinate(1, 0), Coordinate(2, 6), NONE_BLOCKED)
    assert stepped == Coordinate(1, 1)


def test_the_interceptor_routes_around_barriers() -> None:
    walled = frozenset({Coordinate(1, 1)})
    stepped = interceptor_step(BOARD, Coordinate(1, 0), Coordinate(2, 6), walled)
    assert stepped != Coordinate(1, 1)
    assert stepped in (Coordinate(0, 0), Coordinate(2, 0), Coordinate(1, 0))


def test_the_interceptor_is_registered_for_classification() -> None:
    """The tracker can only best-respond to shapes it scores; the interceptor must be
    one of them, and last — on equal evidence assume the simpler pursuer."""
    assert list(PURSUERS) == ["greedy", "herding", "anticipating", "interceptor"]


def test_one_wall_trap_flags_a_cell_inside_walling_range() -> None:
    """A cell the Police can wall directly is a capture the moment we stand on it."""
    assert one_wall_trap(BOARD, Coordinate(1, 1), Coordinate(1, 2), ())


def test_one_wall_trap_flags_a_single_exit_cell_whose_exit_is_sealable() -> None:
    corner = Coordinate(0, 0)
    walls = {Coordinate(1, 0)}
    assert one_wall_trap(BOARD, corner, Coordinate(0, 2), walls), \
        "(0,1) is the corner's last exit and sits one step from the believed Police"


def test_one_wall_trap_ignores_a_distant_police() -> None:
    assert not one_wall_trap(BOARD, Coordinate(0, 0), Coordinate(5, 5), {Coordinate(1, 0)})


def test_wall_pressure_grades_the_seal_cascade() -> None:
    """The waller grid's kill pattern is two seals: 2 exits → 1 → dead. Pressure 1 is
    the grade that has to be refused a step early, and far from the Police the value
    is simply the current mobility — the ranking is untouched where there is no threat."""
    corner = Coordinate(0, 0)
    assert wall_pressure(BOARD, corner, Coordinate(0, 2), ()) == 1, \
        "two exits, one sealable by the in-range wall at (0,1)"
    assert wall_pressure(BOARD, corner, Coordinate(4, 4), ()) == 2, \
        "out of walling range the corner keeps both exits"
    assert wall_pressure(BOARD, corner, Coordinate(0, 2), {Coordinate(1, 0)}) == 0, \
        "one exit left and it is sealable: the next wall ends the game"


def test_wall_risk_leads_the_live_ranking() -> None:
    """Cornered at (0,1) with the Police believed at (0,3): stepping to (0,2) walks
    into walling range and is refused for the safe west corner, whatever the
    distance-plus-mobility comfort of the risky cell."""
    from p2p_thief_agent.strategy.adaptive_policy import PursuerTracker

    belief = [[0.0] * 7 for _ in range(7)]
    belief[0][3] = 1.0
    chosen = adaptive_policy.choose_adaptive_action(
        BOARD, Coordinate(0, 1), belief, PursuerTracker(35), step=1, barriers=())
    target = {Action.WEST: Coordinate(0, 0), Action.STAY: Coordinate(0, 1),
              Action.EAST: Coordinate(0, 2), Action.SOUTH: Coordinate(1, 1)}[chosen]
    assert not one_wall_trap(BOARD, target, Coordinate(0, 3), ()), \
        f"{chosen} lands on {target}, inside the believed Police's walling range"


def _cop_message(step: int, cop_cell: Coordinate) -> dict:
    trail = deposit(blank_field(BOARD), BOARD, cop_cell)
    window = {(r, c): trail[r][c]
              for r in range(BOARD.size) for c in range(BOARD.size) if trail[r][c] > 0}
    return {"step": step, "sender": "police", "hint": "closing in",
            "smell_grid": encode_smell_grid(window), "commit": "0" * 64,
            "timestamp": f"t{step}"}


def test_a_raising_strategy_yields_a_truthful_stay(monkeypatch) -> None:
    """`M6-033`: an uncaught strategy raise reaches the watchdog as a freeze and
    scores the technical 0/0 — strictly worse than any legal move. The fail-safe
    seals a truthful STAY and the game continues."""
    def poisoned(*_args, **_kwargs):
        raise RuntimeError("injected strategy failure")

    # The live turn reaches the shipped policy through `evasion_action`, which binds
    # `choose_adaptive_action` in the barrier_aware_policy namespace — patch it where it is
    # actually looked up so the injected failure reaches the fail-safe (the assertions below
    # are unchanged: a raising strategy must still seal a truthful STAY).
    from p2p_thief_agent.strategy import barrier_aware_policy  # noqa: PLC0415

    monkeypatch.setattr(barrier_aware_policy, "choose_adaptive_action", poisoned)
    decide = thief_policy.make_decide(start=(3, 3))
    message, sealed = decide(_cop_message(1, Coordinate(3, 1)), 1)
    assert sealed["payload"]["move"] == "MOVE:STAY"
    assert sealed["payload"]["position"] == [3, 3], "the sealed record stays truthful"
    assert message["smell_grid"], "the involuntary emission still reaches the wire"
