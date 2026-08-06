"""What the live screen is allowed to know (`M8-001`, `M8-001d`, `M8-007a`).

The highest-consequence boundary in this repository. Appendix E:

* **Rule 8 (Mandatory)** — "Display true local information only in the live user interface.
  Sanction: **Disqualification due to data breach**."
* **Rule 9 (Prohibited)** — "Do not display the full objective board state in the live user
  interface. Sanction: **Project disqualification** due to unfair advantage."

Rule 9 costs the project, not a game. Asked directly, the prohibition is exact: the GUI
"may never show the actual, objective coordinates of the opponent while the match is live",
and it never becomes permitted — after the reveal the operator moves to the **replay
viewer**, which is where seeing the verified history belongs.

**Why a closed type rather than a convention.** This process legitimately holds the
opponent's revealed positions once the audit runs, so a screen that renders whatever the
runtime has would leak them while looking like ordinary code — a silent failure with a
terminal sanction, and no screenshot taken afterwards can prove what was on screen during
the match. `:1647`: each interface shows "only the information accessible to it … and never
the full objective board state. There is no 'bird's-eye view'."

The reference enforces it the same way — its snapshot fixes which fields cross to the GUI,
so the opponent's position "is not part of the View object and the GUI is therefore
incapable of drawing it".

**This is the Thief's screen, so the roles are inverted.** Our own marker is `T`; the
inference we draw is about the *police*, marked `C?`. Taking the companion repository's
version would have produced a Thief window that labels its own cell `C` and guesses at a
thief — backwards in a way that reads as correct at a glance. `THIEF-002` forbids reading
that repository anyway; this is why the rule is worth keeping rather than merely obeying.

**Barriers (`M8-007a`).** Rule 15 (Mandatory) — "Declare openly the placement of all
obstacles" — makes a barrier public *once declared*, so `disclosed_barriers` is the
snapshot's own input rather than something read from a board that knows them all.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum

Cell = tuple[int, int]
Grid = Sequence[Sequence[float]]


class TurnState(Enum):
    """What the banner says, and whether the operator may act.

    Figure 9 names the two the book requires (`:1669`, `:1670`). Locking is mandatory, not
    decorative: asked directly, the interface "enforces the lock" once the commit is sent,
    to stop both sides acting on the same turn.
    """

    YOUR_TURN = ("YOUR TURN", "turn received (act enabled)", True)
    LOCKED = ("LOCKED", "commit sent (input locked)", False)
    WAITING = ("WAITING", "awaiting the opponent's turn", False)
    GAME_OVER = ("GAME OVER", "the sub-game has ended", False)

    def __init__(self, label: str, detail: str, accepts_input: bool) -> None:
        self.label = label
        self.detail = detail
        self.accepts_input = accepts_input


@dataclass(frozen=True)
class LocalTruth:
    """Everything the live screen may see, and nothing else.

    `belief` is a row-major matrix because that is this repository's native shape
    (`perception.belief` works in `Sequence[Sequence[float]]`); converting it to a cell map
    just to match another codebase would add a translation nobody needs and a place for an
    index to flip.
    """

    grid_size: int
    own_position: Cell
    turn_state: TurnState
    step: int
    disclosed_barriers: frozenset[Cell] = frozenset()
    visited: frozenset[Cell] = frozenset()
    belief: Grid = field(default_factory=tuple)
    hints: Sequence[str] = ()
    score: int = 0

    def probability(self, cell: Cell) -> float:
        """Our belief that the police are here. Zero when we have no matrix yet."""
        row, column = cell
        if not self.belief or row >= len(self.belief):
            return 0.0
        line = self.belief[row]
        return float(line[column]) if column < len(line) else 0.0

    @property
    def peak(self) -> float:
        """The strongest belief on the board — the heat ramp is relative to it."""
        return max((float(value) for row in self.belief for value in row), default=0.0)

    @property
    def most_likely(self) -> Cell | None:
        """The cell we read as "probably the police".

        Still not their position: it is *our inference*. Rules 8 and 9 forbid displaying
        the opponent's truth, not displaying a guess — the guess is what a trust map is.
        """
        best, where = 0.0, None
        for row, line in enumerate(self.belief):
            for column, value in enumerate(line):
                if float(value) > best:
                    best, where = float(value), (row, column)
        return where


def local_truth(
    *,
    grid_size: int,
    own_position: Cell,
    turn_state: TurnState,
    step: int,
    disclosed_barriers: Iterable[Cell] = (),
    visited: Iterable[Cell] = (),
    belief: Grid | None = None,
    hints: Iterable[str] = (),
    score: int = 0,
) -> LocalTruth:
    """Build a snapshot from **explicit values**, never by reading a runtime object.

    Keyword-only and exhaustive, so handing the screen a new piece of information is a
    named, visible act. Passing a runtime and letting the view take what it likes is the
    shape of code that eventually takes too much.
    """
    if grid_size <= 0:
        raise ValueError("grid_size must be positive")
    row, column = own_position
    if not (0 <= row < grid_size and 0 <= column < grid_size):
        raise ValueError(f"own_position {own_position} is off a {grid_size}x{grid_size} board")
    return LocalTruth(
        grid_size=grid_size,
        own_position=own_position,
        turn_state=turn_state,
        step=step,
        disclosed_barriers=frozenset(disclosed_barriers),
        visited=frozenset(visited),
        belief=tuple(tuple(float(value) for value in row) for row in (belief or ())),
        hints=tuple(hints),
        score=score,
    )
