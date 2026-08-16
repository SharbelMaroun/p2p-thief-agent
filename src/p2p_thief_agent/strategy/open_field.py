"""Evasion that defends REACHABLE SPACE rather than distance (`open_field_v3`).

Written 2026-08-17 against a threat that is measured rather than imagined. Run 7 finished
6-0, and the reason our three Thief sub-games were survivals is that yanell11's Cop has
never once placed a barrier -- 0 of 14, in every game either side has played. Meanwhile our
own Cop won its three by placing 10 and herding their Thief up the left column into [1,0].
Their logs contain that lesson three times over.

So the honest test is our Thief against OUR Cop, and it loses every arrangement:

    cop=engine        thief=current            COP @19   landed on the Thief
    cop=engine        thief=barrier_aware_v2   COP @21   walled the Thief's cell
    cop=shrink-stack  thief=current            COP @35   walled the Thief's cell
    cop=shrink-stack  thief=barrier_aware_v2   COP @32   walled the Thief's cell

Three of four are barrier kills. Distance-maximising evasion cannot see them coming,
because a wall does not change how far away the Cop is -- it changes how much board is
left. The old policy spent 15 of 35 turns on an edge in run 7 and finished oscillating in
a two-cell pocket; that survived only because nobody closed the door.

**What this policy maximises instead.** For each legal move, flood-fill the region the
Thief can still reach before the Cop could cut it off -- cells strictly nearer to us than
to the pursuer, with barriers as walls. That single quantity captures all three failures
the old policy could not see:

* a corner is bad *before* you are trapped in it, because the region is already small;
* a barrier is bad the moment it is placed, not when it lands on you;
* an edge is mildly bad always, since half the neighbourhood is off-board.

**Adjacency is treated as losing, not risky.** The Cop moves first in every sub-game where
it initiates the turn exchange, so ending a turn beside it means it simply steps on. Moves
that leave us adjacent are excluded outright whenever any alternative exists -- the old
policy chose STAY at distance 1 four times in run 4 and was captured for it.

Nothing here reads a true position: the pursuer's cell comes from our own belief, which is
built from the emissions it publishes.
"""

from __future__ import annotations

from collections import deque

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Action, Coordinate
from p2p_thief_agent.domain.movement import legal_actions, resolve_move

# How far the flood fill looks. The horizon is 35 and the board is 7x7, so a full fill is
# cheap; the cap exists so the cost stays flat if a larger board is ever negotiated.
FILL_LIMIT = 64


def _neighbours(board: Board, cell: Coordinate, blocked: frozenset[Coordinate]):
    for drow, dcol in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nxt = Coordinate(cell.row + drow, cell.col + dcol)
        if board.contains(nxt) and nxt not in blocked:
            yield nxt


def reachable_room(board: Board, thief: Coordinate, cop: Coordinate,
                   blocked: frozenset[Coordinate]) -> int:
    """Count cells the Thief reaches strictly before the Cop, barriers acting as walls.

    A contested Voronoi region, computed by two breadth-first sweeps. It is the quantity a
    cornered agent has already lost and a free one still holds, and unlike Manhattan
    distance it *falls* the moment a barrier goes down -- which is the whole point.
    """
    def sweep(origin: Coordinate) -> dict[Coordinate, int]:
        seen = {origin: 0}
        queue = deque([origin])
        while queue and len(seen) < FILL_LIMIT:
            cell = queue.popleft()
            for nxt in _neighbours(board, cell, blocked):
                if nxt not in seen:
                    seen[nxt] = seen[cell] + 1
                    queue.append(nxt)
        return seen

    ours, theirs = sweep(thief), sweep(cop)
    return sum(1 for cell, cost in ours.items()
               if cost < theirs.get(cell, FILL_LIMIT + 1))


def _breathing_room(board: Board, cell: Coordinate, blocked: frozenset[Coordinate]) -> int:
    """How many ways out this cell has. A corner has two; the middle of the board has four.

    Used only as a tie-break. The region count already prefers open ground, but two moves
    can tie on region while differing in immediate optionality, and the one that keeps more
    doors open is the one that survives an unlucky barrier.
    """
    return sum(1 for _ in _neighbours(board, cell, blocked))


def choose_open_field_action(
    board: Board, position: Coordinate, belief, tracker, step: int,
    blocked: frozenset[Coordinate], *, threshold: int, quota_remaining: int,
) -> Action:
    """Return the move that keeps the most reachable board, never ending adjacent.

    Deterministic throughout: candidates are evaluated in fixed `Action` order and every
    tie is broken by an explicit key, so one message sequence always reproduces one game.
    """
    from p2p_thief_agent.strategy.belief_policy import believed_cop_cell  # noqa: PLC0415

    try:
        cop = believed_cop_cell(belief, board)
    except Exception:  # noqa: BLE001 - a belief problem costs the sharpener, not the move
        cop = None

    candidates = []
    for action in legal_actions(board, position, blocked):
        try:
            cell = resolve_move(board, position, action, blocked)
        except Exception:  # noqa: BLE001 - skip anything the domain refuses
            continue
        if cop is None:
            candidates.append((0, 0, 0, action))
            continue
        gap = abs(cell.row - cop.row) + abs(cell.col - cop.col)
        room = reachable_room(board, cell, cop, blocked)
        candidates.append((gap, room, _breathing_room(board, cell, blocked), action))

    if not candidates:
        return Action.STAY
    if cop is None:
        return candidates[0][3]

    # Adjacency is losing, not merely close: the Cop moves first, so a cell one step away
    # is a cell it steps onto. Drop those unless they are all that is left.
    safe = [c for c in candidates if c[0] > 1] or candidates
    # Distance 2 is the *wall* range, and it is a separate danger from distance 1 being the
    # step-on range. A barrier is placed adjacent to the Cop, so from two cells away it
    # closes to one and seals us on the following turn -- we get exactly one move's warning.
    # At three or more we have two, which is the difference between being herded and being
    # trapped. Measured: `shrink-stack` ringed [3,3]'s eight neighbours and this policy
    # walked into [4,3], the last gap, at distance 3-but-closing; every earlier arm died the
    # same way. So being out of wall range is preferred BEFORE region size -- a large region
    # you are about to be sealed inside is not room, it is a box with the lid open.
    safe.sort(key=lambda c: (c[0] < 3, -c[1], -c[2], -c[0], c[3].value))
    return safe[0][3]
