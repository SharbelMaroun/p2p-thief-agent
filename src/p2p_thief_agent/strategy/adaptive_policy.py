"""The sixth attempt at the anticipating-Cop gap — kept as a measured negative (`M6-030`).

**This policy is not wired into the live loop, and the numbers are why.** It watches
the believed Cop, classifies it against the three committed archetypes, and
best-responds with exact escape sets. Measured on the pursuer grid
(`scripts/experiment_pursuers.py`, 24 paired perimeter openings):

| arm | greedy | herding | anticipating |
| --- | ---: | ---: | ---: |
| shipped `distance + mobility` | 23/24 | 8/24 | 5/24 |
| this policy (argmax-fed) | 23/24 | 4/24 | 4/24 |
| this policy (top-2 uncertainty set) | 23/24 | 2/24 | 4/24 |
| **this policy (truth-fed)** | **24/24** | **24/24** | **24/24** |

The last row is the finding that outlives the failure. Fed the Cop's true cell, the
classifier-plus-solver reaches the theoretical ceiling against *every* archetype —
the sixth attempt's machinery is provably correct, and the previous report's claim
that the belief is "not the bottleneck" is refuted: an argmax that is exact only
37–64% of the time reduces a perfect planner to worse than the shipped heuristic,
because an exact escape line re-planned from a wrong cell walks into the real
pursuer. Planning against a top-2 uncertainty set (`plausible_cells`) was measured
too and is *worse* — the true cell is outside the set often enough that the
intersection empties and the knife-edge moves remain. All six failed attempts now
share one diagnosis, measured rather than guessed: **the estimator is the gap.**
The seventh attempt should sharpen perception — the emission physics are known and
deterministic, so a model-matched likelihood can localise the emitter far better
than raw intensity weighting — and only then re-run this grid; the machinery here
is committed and reproducible precisely so that re-run is one command.

Mechanics, unchanged by the verdict: per turn the tracker scores each archetype by
accumulated negative Manhattan error between its retro-prediction and the newly
believed cell (integer, no tuned weights; disclosed-barrier changes empty the solver
memos because they change the graph); the policy prefers the best-fit model's escape
set, then actions escaping under more models, then the shipped ranking — so with no
escape anywhere it degrades to exactly `choose_evasive_action`. Always legal, and
**history-deterministic**: identical observation sequences give identical actions,
which is what the audit model leaves free and the determinism tests can pin
(adaptation itself is a graded success metric — pp. 94/211, 38/101).
"""

from __future__ import annotations

from collections.abc import Iterable

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.baseline import _ACTION_ORDER, is_dead_end, mobility
from p2p_thief_agent.strategy.belief_policy import Grid, believed_cop_cell
from p2p_thief_agent.strategy.escape_search import Memo, escape_actions
from p2p_thief_agent.strategy.metrics import manhattan_distance
from p2p_thief_agent.strategy.pursuer_models import PURSUERS


class PursuerTracker:
    """Per-sub-game memory: model scores, solver memos, and the last believed cell.

    One tracker per sub-game, owned by the caller — rule 2 forbids shared memory
    between parties, and a module-level tracker would be the easiest accidental way
    to leak one match's inference into the next.
    """

    def __init__(self, horizon: int = 35, memos: dict[str, Memo] | None = None) -> None:
        if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
            raise ValueError(f"horizon must be a positive integer, got {horizon!r}")
        self.horizon = horizon
        self.scores: dict[str, int] = dict.fromkeys(PURSUERS, 0)
        # `memos` may be injected by a measurement harness so the solver table is
        # shared across many games of one configuration — the table depends only on
        # (model, board, barriers), never on a game's history, so sharing changes
        # nothing but speed. Live play passes nothing and keeps per-match isolation.
        self._memos: dict[str, Memo] = memos if memos is not None else {name: {} for name in PURSUERS}
        self._last_believed: Coordinate | None = None
        self._last_blocked: frozenset[Coordinate] = frozenset()

    def observe(self, board: Board, believed: Coordinate, chased: Coordinate,
                blocked: frozenset[Coordinate]) -> None:
        """Score each model against the believed Cop's newest step.

        ``chased`` is our current cell — the position the Cop's just-made move was
        actually pursuing. A barrier change empties the solver memos: the cached
        escape answers were computed on a graph that no longer exists.
        """
        if blocked != self._last_blocked:
            self._memos = {name: {} for name in PURSUERS}
            self._last_blocked = blocked
        if self._last_believed is not None:
            for name, model in PURSUERS.items():
                predicted = model(board, self._last_believed, chased, blocked)
                self.scores[name] -= manhattan_distance(predicted, believed)
        self._last_believed = believed

    def best(self) -> str:
        """The best-fitting archetype; ties resolve to the simplest (greedy first)."""
        return max(PURSUERS, key=lambda name: (self.scores[name],
                                               -list(PURSUERS).index(name)))

    def memo(self, name: str) -> Memo:
        return self._memos[name]


def plausible_cells(belief: Grid, board: Board, count: int = 1) -> tuple[Coordinate, ...]:
    """The ``count`` most probable Cop cells, argmax first, ties row-major.

    The planner's state uncertainty set. Measured honestly: requiring escape from the
    top **2** cells scores *worse* than the argmax alone (herding 2/24 v 4/24) — when
    the true cell is outside the set, intersecting only empties the escape sets — so
    the default is 1 and the knob exists for the estimator-upgrade re-run, not for
    tuning around a broken estimate.
    """
    ranked = sorted(
        ((r, c) for r in range(len(belief)) for c in range(len(belief[0]))),
        key=lambda rc: (-belief[rc[0]][rc[1]], rc[0], rc[1]),
    )
    return tuple(Coordinate(board.min_index + r, board.min_index + c)
                 for r, c in ranked[:count])


def choose_adaptive_action(
    board: Board,
    position: Coordinate,
    belief: Grid,
    tracker: PursuerTracker,
    step: int,
    barriers: Iterable[Coordinate] = (),
    uncertainty: int = 1,
) -> Action:
    """Return the best legal action against the pursuer the evidence says we face."""
    blocked = frozenset(barriers)
    board.validate_position(position)
    believed = believed_cop_cell(belief, board)
    tracker.observe(board, believed, position, blocked)

    remaining = max(tracker.horizon - step, 0)
    cells = plausible_cells(belief, board, uncertainty)
    escapes = {
        name: frozenset.intersection(*(
            frozenset(escape_actions(board, model, position, cell, remaining,
                                     blocked, tracker.memo(name)))
            for cell in cells
        ))
        for name, model in PURSUERS.items()
    }
    favourite = escapes[tracker.best()]
    legal = legal_actions(board, position, blocked)
    targets = {action: resolve_move(board, position, action, blocked) for action in legal}

    def rank(action: Action) -> tuple:
        target = targets[action]
        shipped = (is_dead_end(board, target, position, blocked),
                   -(manhattan_distance(target, believed) + mobility(board, target, blocked)),
                   _ACTION_ORDER.index(action))
        return (action not in favourite,
                -sum(1 for actions in escapes.values() if action in actions),
                *shipped)

    return min(legal, key=rank)
