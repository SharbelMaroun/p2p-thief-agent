"""`M6-010b` companion: *why* physical evidence wins, and where a hint still decides.

`test_strategy_observations.py` asserts the book's outcome — the Thief flees the scent
and not the lie. This file pins the ordering underneath it, because the outcome alone
does not say which mechanism produced it.

Written after probing showed the **Cop repository reaches the identical ordering** from
a different data structure entirely (a dict of cells against this grid of rows). Two
implementations agreeing by construction is worth locking down: without these tests
either side could drift and the parity would break silently, since nothing on the wire
carries belief (`M6-016`) and no handshake could ever detect it.

The ordering is lexicographic, matching the weight-free policies in `M6-004h`:

1. **Scent decides wherever it can.** A located peak concentrates likelihood on one
   cell; a bearing spreads it across half the board.
2. **A hint decides only what scent leaves open** — a tie between equal peaks.

Neither step is stated in the sources. `inst/police_thief_p2p_Summary.md:508` requires
only that a contradicted hint lower trust *and* update the map; `:1020` gives the
behaviour ("the pursuer **ignores** the verbal claim and **continues** to track the
actual scent source"). No trust floor is defined anywhere, so the decay schedule and the
`[0, 1]` clamp are engineering, not scripture.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.field import scent_likelihood
from p2p_thief_agent.perception.hint import decode_hint
from p2p_thief_agent.perception.trust import trust_weighted

N = 7
BOARD = Board(size=N)
CELLS = [(r, c) for r in range(N) for c in range(N)]
THE_LIE = "the cop is south"


def _argmax(grid) -> tuple[int, int]:
    return max(CELLS, key=lambda cell: grid[cell[0]][cell[1]])


def _believe(scent: dict[tuple[int, int], float]):
    return apply_evidence(uniform_belief(N, N), scent_likelihood(scent, BOARD))


def test_a_wisp_of_scent_still_beats_a_lie_believed_completely() -> None:
    """Even the faintest value in the book's emission table outweighs a contradicting
    claim held at **complete** trust. The dominance is structural, not a trust effect —
    which means the `M6-010b` outcome test would pass even with trust disabled, and is
    why this file exists alongside it."""
    for trace in (0.9, 0.2, 0.04):
        believed = apply_evidence(_believe({(0, 0): trace}), trust_weighted(_lie(), 1.0))
        assert _argmax(believed) == (0, 0), trace


def test_a_hint_decides_only_what_the_scent_leaves_open() -> None:
    """Two identical peaks, north and south. Scent cannot choose between them and the
    claim breaks the tie — which is what keeps the verbal layer from being dead code,
    given the test above forbids it from ever overruling scent."""
    tied = _believe({(0, 3): 0.9, (6, 3): 0.9})
    assert _argmax(tied) == (0, 3)
    assert _argmax(apply_evidence(tied, trust_weighted(_lie(), 1.0))) == (6, 3)


def _lie():
    return decode_hint(THE_LIE, N, N)
