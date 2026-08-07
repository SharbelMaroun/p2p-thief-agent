"""The live screen as data (`M8-001a`, `M8-001b`, `M8-006b`, `M8-007`).

Turns a `LocalTruth` snapshot into display-ready values; `ui/live_app.py` reads nothing
else. A Tk window cannot be asserted about in CI, so everything the mandatory belief-map
screenshot claims is decided here.

**The heat ramp scales to the current peak (`M8-001a`).** White at zero, deep red
`(255, 51, 51)` at the peak, matching the reference's own scale. Relative rather than
absolute, and the reason is measurable: belief spread over an 8x8 board peaks near 0.016
at the start, so an absolute ramp would render an honest board uniformly white and the
trust map would never show heat. `:1660` asks that "cells with high probability" stand out
— a statement about contrast, not about absolute values.

**Colour is not the only signal (`M8-011b`).** Every believed cell also carries a
percentage, and the most likely one is marked `C?`. A greyscale print or a red-green
deficiency loses nothing, which is what the accessibility row asks for.

**The marks are the Thief's.** Our own cell is `T`; the inference is about the police, so
it reads `C?`. The companion repository's are the mirror image, and swapping them would
produce a screen that looks right and says the opposite.
"""

from __future__ import annotations

from dataclasses import dataclass

from p2p_thief_agent.live.local_truth import Cell, LocalTruth, TurnState

BANNER_COLOURS = {
    TurnState.YOUR_TURN: "#2ecc71",
    TurnState.LOCKED: "#95a5a6",
    TurnState.WAITING: "#95a5a6",
    TurnState.GAME_OVER: "#546e7a",
}
OWN_MARK = "T"
LIKELY_MARK = "C?"
BARRIER_MARK = "#"
OWN_COLOUR = "#e67e22"      # the reference paints the thief orange
BARRIER_COLOUR = "#263238"
GRID_LINE = "#cccccc"
VISITED_COLOUR = "#b0bec5"


@dataclass(frozen=True)
class CellView:
    """One board square, ready to draw. Carries our belief, never their truth."""

    cell: Cell
    colour: str
    mark: str
    probability: float
    is_own: bool
    is_barrier: bool
    is_visited: bool

    @property
    def percentage(self) -> str:
        """The second signal (`M8-011b`).

        Below one percent the label degrades to `<1%` rather than rounding to `0%`: a
        board claiming the police are nowhere is the opposite of what the number is for.
        """
        if self.probability <= 0:
            return ""
        return "<1%" if self.probability < 0.01 else f"{self.probability * 100:.0f}%"


@dataclass(frozen=True)
class LiveFrame:
    """The whole live screen for one moment."""

    grid_size: int
    banner_label: str
    banner_detail: str
    banner_colour: str
    accepts_input: bool
    step: int
    score: int
    hints: tuple[str, ...]
    cells: tuple[CellView, ...]

    @property
    def status_line(self) -> str:
        return f"step {self.step}   ·   score {self.score}"

    def at(self, cell: Cell) -> CellView:
        return next(view for view in self.cells if view.cell == cell)


def heat_colour(probability: float, peak: float) -> str:
    """White at zero, deep red at the peak.

    A zero peak — nothing believed yet — leaves the board white rather than dividing by
    zero, and a probability above the peak clamps instead of computing a channel Tk would
    refuse and taking the window down mid-match.
    """
    if peak <= 0 or probability <= 0:
        return "#ffffff"
    share = min(probability / peak, 1.0)
    channel = round(255 - (255 - 51) * share)
    return f"#ff{channel:02x}{channel:02x}"


def _cell_view(cell: Cell, truth: LocalTruth, peak: float, likely: Cell | None) -> CellView:
    probability = truth.probability(cell)
    is_own = cell == truth.own_position
    is_barrier = cell in truth.disclosed_barriers
    if is_barrier:
        colour, mark = BARRIER_COLOUR, BARRIER_MARK
    elif is_own:
        colour, mark = OWN_COLOUR, OWN_MARK
    else:
        colour = heat_colour(probability, peak)
        mark = LIKELY_MARK if cell == likely and probability > 0 else ""
    return CellView(
        cell=cell,
        colour=colour,
        mark=mark,
        probability=probability,
        is_own=is_own,
        is_barrier=is_barrier,
        is_visited=cell in truth.visited,
    )


def frame_of(truth: LocalTruth) -> LiveFrame:
    """Project a snapshot onto the screen. Reads only what `LocalTruth` permits."""
    peak, likely = truth.peak, truth.most_likely
    return LiveFrame(
        grid_size=truth.grid_size,
        banner_label=truth.turn_state.label,
        banner_detail=truth.turn_state.detail,
        banner_colour=BANNER_COLOURS[truth.turn_state],
        accepts_input=truth.turn_state.accepts_input,
        step=truth.step,
        score=truth.score,
        hints=tuple(truth.hints),
        cells=tuple(
            _cell_view((row, column), truth, peak, likely)
            for row in range(truth.grid_size)
            for column in range(truth.grid_size)
        ),
    )
