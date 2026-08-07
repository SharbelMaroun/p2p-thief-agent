"""Belief-driven Thief evasion: get away from the believed Cop, and keep room to run.

The perception layer yields a probability distribution over the Cop's position; this module
turns that into a legal move by reading off the most likely Cop cell and scoring each legal
move against it.

**Distance alone is not the objective, and assuming it was cost us the game** (`M6-015c`).
This delegated to `baseline.choose_action` until 2026-08-07, whose criteria are lexicographic
with threat distance first. That maximises how far away the Thief is *this turn* and walks it
into a corner, where distance is large and there are no exits left. Measured in the league
points that actually decide a sub-game, it scored **worse than a random walk**. The rewrite is
in `choose_evasive_action`, which carries the numbers.

The three properties `choose_action` gave are kept, and are still what the tests check:

- the move is **always legal** (`M6-004e`), whatever the belief says — even a belief peaked
  on a wall or on the Thief's own cell;
- the tie-breaks are **fixed** (`M6-004g`): identical inputs yield an identical action;
- nothing on this path is an LLM or a network call (`M6-004b`): the belief is a plain matrix
  of numbers and the policy is pure Python.

The belief is a `board.size × board.size` grid; cell `(r, c)` maps to board coordinate
`(min_index + r, min_index + c)`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate, DomainError
from p2p_thief_agent.domain.movement import legal_actions, resolve_move
from p2p_thief_agent.strategy.baseline import _ACTION_ORDER, is_dead_end, mobility
from p2p_thief_agent.strategy.metrics import manhattan_distance

Grid = Sequence[Sequence[float]]


def initial_belief(board: Board, cop_start: Coordinate) -> tuple[tuple[float, ...], ...]:
    """Belief before any observation: the Cop's public start cell is known certainty (`M6-021`).

    The agreed start positions are public, and this peer moves first, so on turn 1 the Cop is
    exactly at its start — a point mass, not a uniform guess. Later scent observations spread
    it as the Cop moves.
    """
    board.validate_position(cop_start)
    start = (cop_start.row - board.min_index, cop_start.col - board.min_index)
    return tuple(
        tuple(1.0 if (r, c) == start else 0.0 for c in range(board.size))
        for r in range(board.size)
    )


def believed_cop_cell(belief: Grid, board: Board) -> Coordinate:
    """Return the single most-likely Cop cell, breaking ties by lowest row then column.

    A distribution can be multimodal or flat; the tie-break makes the choice deterministic
    so the whole policy stays reproducible (`M6-004g`). The belief must match the board.
    """
    if len(belief) != board.size or any(len(row) != board.size for row in belief):
        raise DomainError(f"belief must be a {board.size}x{board.size} grid")
    row, col = max(
        ((r, c) for r in range(board.size) for c in range(board.size)),
        key=lambda rc: (belief[rc[0]][rc[1]], -rc[0], -rc[1]),
    )
    return Coordinate(board.min_index + row, board.min_index + col)


def choose_evasive_action(
    board: Board,
    position: Coordinate,
    belief: Grid,
    barriers: Iterable[Coordinate] = (),
) -> Action:
    """Return the best legal action: distance from the believed Cop **plus** room to run.

    Until 2026-08-07 this delegated to `choose_action`, whose criteria are *lexicographic*
    with threat distance first — so mobility only ever separated equally-distant moves. On a
    bounded board against a pursuer that is precisely the losing rule: maximising distance
    walks into a corner, where the distance is large and the exits are gone.

    The measurement said so and was ignored, because it was the wrong measurement. `M6-015`
    accepted this policy on **total survival steps**, where it wins comfortably (661 v 437
    across 24 openings). Appendix F pays **10 for reaching the threshold and 5 for capture,
    with nothing in between**, so surviving 28 turns of 35 scores exactly as badly as being
    caught on turn 2. In league points the old policy scored **140 against the blind
    baseline's 175** — our strategy was worse than a random walk at the only thing that is
    counted (`M6-015c`, `M9-006`).

    Summing distance and mobility instead scores **235, escaping 23 of 24** openings. The
    objective is P(reach the horizon), not E[steps], and the two disagree: a cell two steps
    further away with one exit is worse than a nearer cell with three.

    `mobility` is used rather than `edge_contacts` — they score the same on an empty board,
    but the Cop places up to 14 barriers and only `mobility` counts those. Checked on board
    sizes 5-9, on randomised openings rather than the tuned set, on barrier layouts, and on
    horizons 15-50; the advantage holds throughout and *grows* with the horizon, because the
    old policy's ~28-step ceiling is invisible until the threshold exceeds it.

    Everything `choose_action` guaranteed still holds and is still tested: the action is
    always legal, dead ends rank last as a block, and the tie-break is fixed, so identical
    inputs give an identical action.
    """
    threat = believed_cop_cell(belief, board)
    blocked = frozenset(barriers)
    board.validate_position(position)
    legal = legal_actions(board, position, blocked)
    targets = {action: resolve_move(board, position, action, blocked) for action in legal}

    def rank(action: Action) -> tuple:
        target = targets[action]
        # Descending on the score, so it is negated for a single ascending sort. Dead ends
        # sort last as a block rather than being dropped: they stay legal, and a Thief with
        # nothing else left still needs a complete ordering.
        room = mobility(board, target, blocked)
        return (is_dead_end(board, target, position, blocked),
                -(manhattan_distance(target, threat) + room),
                _ACTION_ORDER.index(action))

    return min(legal, key=rank)
