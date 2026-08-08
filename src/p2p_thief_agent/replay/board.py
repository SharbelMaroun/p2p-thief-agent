"""The replay board as data: what really happened, drawn (`M8-016`).

The replay axis exists to answer "what really happened?" (p.54/135) — the book's
"Retrospective Witness". Rule 9's objective-board ban binds the **live** interface;
in the audit phase the nonces are public and the reference viewer itself paints both
true positions on one board when the opponent's log sits beside our own, falling back
to a single trail when it does not. This module is that reconstruction as display-ready
values; the widget layer reads nothing else, and verification stays the cursor's job —
nothing here touches a hash.

Tolerance is the design bar: a viewer that raises on a strange record fails during the
demo it exists for. A record without a position is skipped; barriers come from a
`payload.barriers` list when a log carries one (the companion shape) or are parsed out
of our own `state` string; the grid size is read from the state string with the drawn
coordinates as fallback; an opponent log that does not align by step renders whatever
does.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from p2p_thief_agent.replay.load import ReplayLog

Cell = tuple[int, int]

OUR_COLOUR = "#ef6c00"
THEIR_COLOUR = "#1565c0"
BARRIER_COLOUR = "#263238"
CAPTURE_COLOUR = "#c62828"


@dataclass(frozen=True)
class Trail:
    """One side's revealed path up to the cursor: oldest first, current cell last."""

    label: str
    colour: str
    cells: tuple[Cell, ...]

    @property
    def current(self) -> Cell | None:
        return self.cells[-1] if self.cells else None


@dataclass(frozen=True)
class BoardFrame:
    """The reconstructed board for one cursor position. Display values only."""

    grid_size: int
    ours: Trail
    theirs: Trail
    barriers: frozenset[Cell]
    capture_cell: Cell | None

    @property
    def caption(self) -> str:
        sides = [f"{self.ours.label} trail {len(self.ours.cells)} step(s)"]
        if self.theirs.cells:
            sides.append(f"{self.theirs.label} trail {len(self.theirs.cells)} step(s)")
        else:
            sides.append("opponent log not loaded")
        return "   ·   ".join(sides)


def _payload(record: object) -> Mapping[str, object]:
    payload = record.get("payload") if isinstance(record, Mapping) else None
    return payload if isinstance(payload, Mapping) else {}


def _position(record: object) -> Cell | None:
    value = _payload(record).get("position")
    if isinstance(value, Sequence) and len(value) == 2:
        try:
            return int(value[0]), int(value[1])
        except (TypeError, ValueError):
            return None
    return None


def _step(record: object, default: int) -> int:
    value = _payload(record).get("step")
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def _barriers(record: object) -> frozenset[Cell]:
    """The cumulative disclosed set: a `barriers` list, else our state-string form."""
    payload = _payload(record)
    value = payload.get("barriers")
    if not isinstance(value, Sequence) or isinstance(value, str):
        match = re.search(r"barriers=(\[.*?\])(?:;|$)", str(payload.get("state", "")))
        if match is None:
            return frozenset()
        try:
            value = ast.literal_eval(match.group(1))
        except (ValueError, SyntaxError):
            return frozenset()
    cells = []
    for item in value:
        if isinstance(item, Sequence) and not isinstance(item, str) and len(item) == 2:
            try:
                cells.append((int(item[0]), int(item[1])))
            except (TypeError, ValueError):
                continue
    return frozenset(cells)


def _grid_size(records: Sequence[object], positions: Sequence[Cell]) -> int:
    for record in records:
        match = re.search(r"grid=(\d+)x", str(_payload(record).get("state", "")))
        if match is not None:
            return int(match.group(1))
    reach = max((max(cell) for cell in positions), default=6)
    return max(reach + 1, 7)


def board_frame(
    log: ReplayLog,
    position: int,
    *,
    opponent: ReplayLog | None = None,
    our_label: str = "thief",
    their_label: str = "police",
    captured: bool = False,
) -> BoardFrame:
    """Reconstruct the board at cursor ``position`` (zero-based, clamped).

    Our trail is every revealed position up to the cursor; the opponent's, when that
    log is present, is every record at or before the step under the cursor — the turn
    cycle's own alignment, with the misaligned remainder simply not drawn. ``captured``
    rings our final cell, because the cell we were caught on is the one the audit
    argued about.
    """
    records = log.records
    index = max(0, min(position, len(records) - 1)) if records else 0
    shown = records[: index + 1]
    ours = tuple(cell for cell in (_position(r) for r in shown) if cell is not None)
    step_now = _step(records[index], index + 1) if records else 0
    theirs: tuple[Cell, ...] = ()
    barriers = _barriers(records[index]) if records else frozenset()
    if opponent is not None:
        aligned = [r for r in opponent.records if _step(r, 10**9) <= step_now]
        theirs = tuple(cell for cell in (_position(r) for r in aligned) if cell is not None)
        if aligned:
            barriers = barriers | _barriers(aligned[-1])
    capture_cell = ours[-1] if captured and index == len(records) - 1 and ours else None
    every = [*ours, *theirs]
    return BoardFrame(
        grid_size=_grid_size([*shown, *(opponent.records if opponent else ())], every),
        ours=Trail(our_label, OUR_COLOUR, ours),
        theirs=Trail(their_label, THEIR_COLOUR, theirs),
        barriers=barriers,
        capture_cell=capture_cell,
    )
