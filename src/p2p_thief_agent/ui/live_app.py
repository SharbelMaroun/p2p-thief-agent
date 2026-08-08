"""The live window (`M8-001`, `M8-001b`, `M8-001c`, `M8-007`) — widgets only, no logic.

`:1651`: each side "runs its software from a dedicated GUI (for example, Tkinter or PyQt)".
What it may show is fixed by rules 8 and 9 and enforced by construction: this window reads
`LiveFrame`, which comes from `LocalTruth`, whose field set cannot hold the opponent's real
position. `test_local_truth_boundary.py` asserts both the field set and the import boundary,
because rule 9's sanction is project disqualification and one import would earn it.

**The banner is the state machine made visible (`M8-001b`).** Figure 9 gives both states:
green `YOUR TURN` labelled "turn received (act enabled)", grey `LOCKED` labelled "commit
sent (input locked)". The banner's *colour* is the frame's — semantic and pinned — and only
the chrome around it (`ui/style.py`) is styling. The board card stays light on purpose:
the white-to-red heat ramp is the reference's, and "deeper red = higher probability" is
the meaning a grader reads.

**Locking is enforced, not indicated (`M8-001c`).** The buttons are genuinely disabled,
and a click landing during the repaint is dropped by `_guarded` rather than queued. A
queued move would surface a turn later as an action nobody chose.

Excluded from coverage per `M8-006c`.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import font as tkfont

from p2p_thief_agent.live.view_model import LiveFrame
from p2p_thief_agent.ui.style import (
    ACCENT_WARM,
    BG,
    BOARD_BG,
    BOARD_LINE,
    INK,
    MUTED,
    PANEL,
    PANEL_EDGE,
    apply_icon,
    banner_pill,
    rounded_rect,
    style_button,
)

CELL = 54
MARGIN = 14
_ICON = Path(__file__).resolve().parents[3] / "assets" / "icon.png"
BANNER_W, BANNER_H = 900, 64
MOVES = (("North", "N"), ("South", "S"), ("East", "E"), ("West", "W"), ("Stay", "STAY"))


class LiveWindow:
    """A Tk window over a `LiveFrame`. Holds widgets; derives every string from the frame."""

    def __init__(
        self,
        frame: LiveFrame,
        root: tk.Misc | None = None,
        on_move: Callable[[str], None] | None = None,
    ) -> None:
        self._frame = frame
        self._on_move = on_move
        self.root = root or tk.Tk()
        self.root.title("Live GUI — local truth only")
        self.root.configure(bg=BG)
        self._icon = apply_icon(self.root, _ICON)
        self._mono = tkfont.Font(family="Consolas", size=8)
        self._build()
        self.show(frame)

    def _build(self) -> None:
        self._banner = tk.Canvas(self.root, width=BANNER_W, height=BANNER_H,
                                 bg=BG, highlightthickness=0)
        self._banner.pack(fill="x", padx=10, pady=(10, 0))
        self._status = tk.Label(self.root, font=("Segoe UI", 9, "bold"), bg=BG, fg=MUTED)
        self._status.pack(fill="x", pady=(2, 6))

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=12)
        self._canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        self._canvas.pack(side="left")
        side = tk.Frame(body, bg=PANEL, highlightthickness=1,
                        highlightbackground=PANEL_EDGE)
        side.pack(side="left", fill="both", expand=True, padx=(12, 0))
        tk.Label(side, text="HINTS RECEIVED", font=("Segoe UI", 8, "bold"), bg=PANEL,
                 fg=ACCENT_WARM).pack(anchor="w", padx=10, pady=(8, 2))
        self._hints = tk.Label(side, font=("Segoe UI", 9), bg=PANEL, fg=INK,
                               justify="left", anchor="nw", wraplength=260)
        self._hints.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._legend = tk.Label(self.root, font=("Segoe UI", 8), bg=BG, fg=MUTED)
        self._legend.pack(fill="x", pady=(6, 0))

        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=12, pady=10)
        self._buttons = []
        for name, move in MOVES:
            button = tk.Button(bar, text=name, font=("Segoe UI", 9), width=9,
                               command=self._guarded(move))
            style_button(button, accent=ACCENT_WARM)
            button.pack(side="left", padx=4)
            self._buttons.append(button)

    def _guarded(self, move: str) -> Callable[[], None]:
        """Drop an out-of-turn click rather than queueing it (`M8-001c`)."""
        def handler() -> None:
            if self._frame.accepts_input and self._on_move is not None:
                self._on_move(move)
        return handler

    def show(self, frame: LiveFrame) -> None:
        """Repaint from a frame. The only place widget state is ever set."""
        self._frame = frame
        width = max(BANNER_W, self.root.winfo_width())
        banner_pill(self._banner, width, BANNER_H, frame.banner_colour,
                    frame.banner_label, frame.banner_detail)
        self._status.configure(text=frame.status_line)
        self._hints.configure(text="\n".join(frame.hints) or "— none yet —")
        self._legend.configure(
            text="T = own position   ·   C? = most likely police cell (our inference)"
                 "   ·   # = disclosed barrier   ·   depth of red = probability"
        )
        for button in self._buttons:
            button.configure(state="normal" if frame.accepts_input else "disabled")
        self._paint_board(frame)

    def _paint_board(self, frame: LiveFrame) -> None:
        size = frame.grid_size * CELL
        self._canvas.configure(width=size + 2 * MARGIN, height=size + 2 * MARGIN)
        self._canvas.delete("all")
        rounded_rect(self._canvas, 2, 2, size + 2 * MARGIN - 2, size + 2 * MARGIN - 2,
                     18, fill=BOARD_BG, outline=PANEL_EDGE)
        for view in frame.cells:
            row, column = view.cell
            x, y = MARGIN + column * CELL, MARGIN + row * CELL
            rounded_rect(self._canvas, x + 2, y + 2, x + CELL - 2, y + CELL - 2, 10,
                         fill=view.colour, outline=BOARD_LINE)
            if view.is_visited and not view.is_own and not view.is_barrier:
                self._canvas.create_oval(x + 24, y + 24, x + 30, y + 30,
                                         fill="#b0bec5", outline="")
            if view.mark:
                self._canvas.create_text(
                    x + CELL / 2, y + CELL / 2 - 6, text=view.mark,
                    font=("Segoe UI", 10, "bold"),
                    fill="#ffffff" if view.is_own or view.is_barrier else "#1e293b")
            # Sub-1% labels on every cell buried the signal in a page of "<1%"s; the
            # number stays wherever it means something — any cell at 1%+ and the marked
            # cell — so colour is still not the only signal without the noise.
            if view.percentage and (view.mark or view.probability >= 0.01):
                self._canvas.create_text(x + CELL / 2, y + CELL - 12, text=view.percentage,
                                         font=self._mono, fill="#64748b")


def run(frame: LiveFrame) -> None:  # pragma: no cover - the event loop
    LiveWindow(frame).root.mainloop()
