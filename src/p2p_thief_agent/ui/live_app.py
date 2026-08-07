"""The live window (`M8-001`, `M8-001b`, `M8-001c`, `M8-007`) — widgets only, no logic.

`:1651`: each side "runs its software from a dedicated GUI (for example, Tkinter or PyQt)".
What it may show is fixed by rules 8 and 9 and enforced by construction: this window reads
`LiveFrame`, which comes from `LocalTruth`, whose field set cannot hold the opponent's real
position. `test_local_truth_boundary.py` asserts both the field set and the import boundary,
because rule 9's sanction is project disqualification and one import would earn it.

**The banner is the state machine made visible (`M8-001b`).** Figure 9 gives both states:
green `YOUR TURN` labelled "turn received (act enabled)", grey `LOCKED` labelled "commit
sent (input locked)".

**Locking is enforced, not indicated (`M8-001c`).** The row's condition is that out-of-turn
input is "ignored", and asked directly the interface "enforces the lock" after the commit
to prevent both sides acting on one turn — so the buttons are genuinely disabled, and a
click landing during the repaint is dropped by `_guarded` rather than queued. A queued move
would surface a turn later as an action nobody chose.

Excluded from coverage per `M8-006c`.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import font as tkfont

from p2p_thief_agent.live.view_model import LiveFrame

BACKGROUND = "#eceff1"
PANEL = "#ffffff"
INK = "#263238"
MUTED = "#607d8b"
CELL = 54
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
        self.root.configure(bg=BACKGROUND)
        self._mono = tkfont.Font(family="Consolas", size=8)
        self._build()
        self.show(frame)

    def _build(self) -> None:
        self._banner = tk.Label(self.root, font=("Segoe UI", 18, "bold"), fg="#ffffff", pady=8)
        self._banner.pack(fill="x")
        self._detail = tk.Label(self.root, font=("Segoe UI", 9), bg=BACKGROUND, fg=INK)
        self._detail.pack(fill="x", pady=(4, 0))
        self._status = tk.Label(self.root, font=("Segoe UI", 9, "bold"), bg=BACKGROUND, fg=INK)
        self._status.pack(fill="x", pady=(0, 6))

        body = tk.Frame(self.root, bg=BACKGROUND)
        body.pack(fill="both", expand=True, padx=10)
        self._canvas = tk.Canvas(body, bg=PANEL, highlightthickness=1,
                                 highlightbackground="#b0bec5")
        self._canvas.pack(side="left")
        side = tk.Frame(body, bg=PANEL, bd=1, relief="solid")
        side.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(side, text="HINTS RECEIVED", font=("Segoe UI", 8, "bold"), bg=PANEL,
                 fg=MUTED).pack(anchor="w", padx=8, pady=(6, 2))
        self._hints = tk.Label(side, font=("Segoe UI", 9), bg=PANEL, fg=INK, justify="left",
                               anchor="nw", wraplength=260)
        self._hints.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._legend = tk.Label(self.root, font=("Segoe UI", 8), bg=BACKGROUND, fg=MUTED)
        self._legend.pack(fill="x", pady=(4, 0))

        bar = tk.Frame(self.root, bg=BACKGROUND)
        bar.pack(fill="x", padx=10, pady=8)
        self._buttons = [
            tk.Button(bar, text=name, font=("Segoe UI", 9), width=10,
                      command=self._guarded(move))
            for name, move in MOVES
        ]
        for button in self._buttons:
            button.pack(side="left", padx=3)

    def _guarded(self, move: str) -> Callable[[], None]:
        """Drop an out-of-turn click rather than queueing it (`M8-001c`)."""
        def handler() -> None:
            if self._frame.accepts_input and self._on_move is not None:
                self._on_move(move)
        return handler

    def show(self, frame: LiveFrame) -> None:
        """Repaint from a frame. The only place widget state is ever set."""
        self._frame = frame
        self._banner.configure(text=f"  {frame.banner_label}  ", bg=frame.banner_colour)
        self._detail.configure(text=frame.banner_detail)
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
        self._canvas.configure(width=size, height=size)
        self._canvas.delete("all")
        for view in frame.cells:
            row, column = view.cell
            x, y = column * CELL, row * CELL
            self._canvas.create_rectangle(x, y, x + CELL, y + CELL,
                                          fill=view.colour, outline="#cccccc")
            if view.is_visited and not view.is_own and not view.is_barrier:
                self._canvas.create_oval(x + 24, y + 24, x + 30, y + 30,
                                         fill="#b0bec5", outline="")
            if view.mark:
                self._canvas.create_text(
                    x + CELL / 2, y + CELL / 2 - 6, text=view.mark,
                    font=("Segoe UI", 10, "bold"),
                    fill="#ffffff" if view.is_own or view.is_barrier else INK)
            if view.percentage:
                self._canvas.create_text(x + CELL / 2, y + CELL - 12, text=view.percentage,
                                         font=self._mono, fill=MUTED)


def run(frame: LiveFrame) -> None:  # pragma: no cover - the event loop
    LiveWindow(frame).root.mainloop()
