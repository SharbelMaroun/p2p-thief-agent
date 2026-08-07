"""The replay window (`M8-002`, `M8-002e`) — widgets only, no logic.

Rule 20 is Mandatory with the sanction "threshold condition for confirmation of logs and
submission of the project" (p.129/272). `replay/` satisfies the verification; this file
satisfies the *app*, and produces the `Verified OK` capture the book calls "absolute
mandatory" in the README report (p.81/189).

**What the screen shows**, asked directly: the `nonce`, `move` and original `commit` from
the log entry (p.56/142); a clear verdict indicator — green `Verified OK` or a bright red
`TAMPERED` banner; and controls to move "back and forth in time" (p.56/141). The board is
**not** required, so this window shows the cryptographic evidence rather than a grid; the
belief map belongs to the live GUI, which is where the book puts it (`M8-015a`).

**Every widget reads `ReplayFrame` and nothing else** (`M8-006`). Excluded from coverage by
`M8-006c`: a Tk window cannot be asserted about in CI, and a test that merely constructs
one proves only that Tk imports. What the screen *claims* is asserted in
`tests/unit/test_replay_view_model.py`.

Controls follow the reference's own set — restart, back, step, and a jump — with one
addition it does not have: **jump to the first divergence**. Once `:1769` has decided a
match there is no appeal, so the only remaining question is which step, and making an
auditor click through a long log to find it is how that answer gets recorded wrong.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from p2p_thief_agent.replay.cursor import Replay
from p2p_thief_agent.replay.view_model import (
    COLOUR_NEUTRAL,
    COLOUR_TEXT_ON_STAMP,
    ReplayFrame,
    frame_of,
)

BACKGROUND = "#eceff1"
PANEL = "#ffffff"
INK = "#263238"
MUTED = "#607d8b"
ROW_OK = "#e8f5e9"
ROW_BAD = "#ffebee"
DETAIL_FIELDS = ("step", "sender", "move", "commit", "nonce", "verdict")


class ReplayWindow:
    """A Tk window over a `Replay`. Holds widgets; derives every string from the frame."""

    def __init__(self, replay: Replay, root: tk.Misc | None = None) -> None:
        self._replay = replay
        self.root = root or tk.Tk()
        self.root.title("Replay Viewer — cryptographic verification")
        self.root.configure(bg=BACKGROUND)
        self._mono = tkfont.Font(family="Consolas", size=9)
        self._build()
        self.refresh()

    # --- widgets ------------------------------------------------------------------------

    def _build(self) -> None:
        self._stamp = tk.Label(self.root, font=("Segoe UI", 22, "bold"),
                               fg=COLOUR_TEXT_ON_STAMP, pady=10)
        self._stamp.pack(fill="x")
        self._banner = tk.Label(self.root, font=("Segoe UI", 10), bg=BACKGROUND, fg=INK)
        self._banner.pack(fill="x", pady=(6, 0))
        self._source = tk.Label(self.root, font=("Segoe UI", 8), bg=BACKGROUND, fg=MUTED)
        self._source.pack(fill="x")
        self._sequence = tk.Label(self.root, font=("Segoe UI", 8), bg=BACKGROUND)
        self._sequence.pack(fill="x", pady=(0, 6))

        body = tk.Frame(self.root, bg=BACKGROUND)
        body.pack(fill="both", expand=True, padx=10)
        self._rows = tk.Frame(body, bg=PANEL, bd=1, relief="solid")
        self._rows.pack(side="left", fill="both", expand=True)
        detail = tk.Frame(body, bg=PANEL, bd=1, relief="solid")
        detail.pack(side="left", fill="both", padx=(10, 0))
        self._detail = self._build_detail(detail)
        self._build_controls()

    def _build_detail(self, parent: tk.Frame) -> dict[str, tk.Label]:
        tk.Label(parent, text="STEP UNDER CURSOR", font=("Segoe UI", 8, "bold"), bg=PANEL,
                 fg=MUTED).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=6)
        labels: dict[str, tk.Label] = {}
        for index, name in enumerate(DETAIL_FIELDS, 1):
            tk.Label(parent, text=name, font=("Segoe UI", 8, "bold"), bg=PANEL,
                     fg=MUTED).grid(row=index, column=0, sticky="nw", padx=(8, 6), pady=2)
            value = tk.Label(parent, font=self._mono, bg=PANEL, fg=INK, justify="left",
                             wraplength=300)
            value.grid(row=index, column=1, sticky="w", padx=(0, 8), pady=2)
            labels[name] = value
        return labels

    def _build_controls(self) -> None:
        bar = tk.Frame(self.root, bg=BACKGROUND)
        bar.pack(fill="x", padx=10, pady=8)
        for text, command in (
            ("|< Restart", self._replay.restart),
            ("< Back", self._replay.step_back),
            ("Step >", self._replay.step_forward),
            ("Jump to divergence", self._replay.go_to_first_divergence),
        ):
            tk.Button(bar, text=text, font=("Segoe UI", 9), width=17,
                      command=self._act(command)).pack(side="left", padx=3)
        self._position = tk.Label(bar, font=("Segoe UI", 9, "bold"), bg=BACKGROUND, fg=INK)
        self._position.pack(side="right")

    def _act(self, command):
        """Every control does the same two things: move, then re-derive the whole screen.

        Re-deriving rather than patching individual labels is what keeps `M8-008a` true at
        the widget layer — the stamp is recomputed on every navigation, so what a
        screenshot photographs is a live computation and not a remembered result.
        """
        def handler() -> None:
            command()
            self.refresh()
        return handler

    # --- rendering ----------------------------------------------------------------------

    def refresh(self) -> None:
        """Repaint from a fresh frame. The only place widget text is ever set."""
        frame = frame_of(self._replay)
        self._stamp.configure(text=f"  {frame.stamp}  ", bg=frame.stamp_colour)
        self._banner.configure(text=frame.banner)
        self._source.configure(text=f"{frame.origin}   ·   game {frame.game_id}"
                                    f"   ·   sub-game {frame.sub_game}")
        self._sequence.configure(text=frame.sequence_summary,
                                 fg=MUTED if frame.sequence_ok else COLOUR_NEUTRAL)
        self._position.configure(text=frame.position_label)
        self._paint_rows(frame)
        current = frame.current
        for name, value in zip(
            DETAIL_FIELDS,
            (current.step, current.sender, current.move, current.commit, current.nonce,
             current.reason),
            strict=True,
        ):
            self._detail[name].configure(text=value)

    def _paint_rows(self, frame: ReplayFrame) -> None:
        for child in self._rows.winfo_children():
            child.destroy()
        for row in frame.rows:
            text = (f"{'>' if row.is_current else ' '} step {row.step:>3}  {row.sender:<7}"
                    f" {row.move:<4} {row.commit_short:<14} {row.verdict}")
            tk.Label(self._rows, text=text, font=self._mono, anchor="w",
                     bg=ROW_OK if row.ok else ROW_BAD, fg=INK,
                     padx=8, pady=1).pack(fill="x")


def run(replay: Replay) -> None:  # pragma: no cover - the event loop
    ReplayWindow(replay).root.mainloop()
