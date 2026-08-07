"""`M6-015` / `M6-015c`: belief-driven evasion beats the blind baseline **in league points**.

A deterministic pursuing Cop (fixed policy, `M6-015a`) chases the Thief; the Cop deposits
scent it cannot help emitting, and the Thief either ignores it (blind baseline) or senses it
and evades. If belief-driven ever failed to beat blind the number would say so and the policy
would be reverted — a negative result is evidence, not something to hide (`M6-015b`).

**The criterion changed on 2026-08-07, and the old one had been passing while the policy
lost.** `M6-015` accepted the policy on *total survival steps* over four hand-picked openings
(125 v 52). Widened to all 24 perimeter openings the steps margin narrowed, and under
Appendix F — **10 for reaching the threshold, 5 for capture, nothing in between** — the
ranking reversed outright: belief 140, blind 175. A policy that reliably survives 28 turns of
35 scores exactly as badly as one caught on turn 2, so steps recommended a strategy the rules
do not reward.

Both metrics are asserted now, and the points one is the binding one. It is measured over the
full opening set rather than four chosen scenarios, because the four were where the old
policy looked best.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.field import blank_field, deposit, scent_likelihood
from p2p_thief_agent.strategy.baseline import choose_action
from p2p_thief_agent.strategy.belief_policy import choose_evasive_action
from p2p_thief_agent.strategy.metrics import manhattan_distance

NO_BARRIERS = frozenset()
SCENARIOS = [
    (Coordinate(0, 0), Coordinate(6, 6)),
    (Coordinate(6, 0), Coordinate(0, 6)),
    (Coordinate(0, 6), Coordinate(6, 0)),
    (Coordinate(3, 0), Coordinate(3, 6)),
]


def _cop_pursues(board: Board, cop: Coordinate, thief: Coordinate) -> Coordinate:
    """Deterministic greedy pursuit: the legal move that minimises distance to the thief."""
    targets = {a: resolve_move(board, cop, a, NO_BARRIERS) for a in legal_actions(board, cop, NO_BARRIERS)}
    return targets[min(targets, key=lambda a: (manhattan_distance(targets[a], thief), a.value))]


def _observed(scent, board: Board) -> dict:
    return {(r, c): scent[r][c] for r in range(board.size) for c in range(board.size) if scent[r][c] > 0}


def _blind(board: Board, thief: Coordinate, _smell: dict):
    return choose_action(board, thief, (), NO_BARRIERS)


def _belief(board: Board, thief: Coordinate, smell: dict):
    belief = uniform_belief(board.size, board.size)
    if smell:
        belief = apply_evidence(belief, scent_likelihood(smell, board))
    return choose_evasive_action(board, thief, belief)


def simulate(board: Board, cop: Coordinate, thief: Coordinate, policy, steps: int) -> int:
    scent = blank_field(board)
    for step in range(1, steps + 1):
        cop = _cop_pursues(board, cop, thief)
        scent = deposit(scent, board, cop)
        if cop == thief:
            return step - 1
        thief = resolve_move(board, thief, policy(board, thief, _observed(scent, board)), NO_BARRIERS)
        if cop == thief:
            return step
    return steps


def run_comparison(board: Board | None = None, steps: int = 35) -> dict:
    board = Board(size=7) if board is None else board
    blind = sum(simulate(board, cop, thief, _blind, steps) for cop, thief in SCENARIOS)
    belief = sum(simulate(board, cop, thief, _belief, steps) for cop, thief in SCENARIOS)
    return {"blind_total_survival": blind, "belief_total_survival": belief,
            "scenarios": len(SCENARIOS), "max_steps": steps}


def test_belief_driven_evasion_beats_the_blind_baseline_in_league_points() -> None:
    """**The binding criterion** (`M6-015c`). Points are what a sub-game pays; steps are
    not. This is asserted over every perimeter opening, not the four the old criterion
    used, because a policy chosen on four scenarios is a policy fitted to four scenarios."""
    from scripts.run_experiments import arms_comparison  # noqa: PLC0415

    report = arms_comparison()
    points = report["league_points"]
    assert points["belief"] > points["blind"], (
        f"belief scores {points['belief']} against blind's {points['blind']}. `M6-015b` "
        "says a policy that does not beat the baseline is reverted, and league points are "
        "the measure that decides a sub-game")


def test_belief_driven_evasion_also_survives_longer() -> None:
    """The original criterion, kept because it is still true and still informative — it
    just cannot be the acceptance test on its own. Steps and points disagreed once and
    would have again."""
    result = run_comparison()
    assert result["belief_total_survival"] > result["blind_total_survival"]


def test_the_two_metrics_are_measured_separately() -> None:
    """A guard against the failure that produced `M6-015c`: if points were derived from
    steps rather than from the outcome, they could never disagree, and the disagreement is
    the finding."""
    from scripts.run_experiments import arms_comparison  # noqa: PLC0415

    report = arms_comparison()
    assert report["survived_full_horizon"]["belief"] > report["survived_full_horizon"]["blind"]
