"""The replay window's evidence panels — building and painting, no logic (`M8-016`).

Split from `replay_app.py` when the styled window crossed the length cap: the app
assembles and navigates, this file builds and paints the panels, and both read only
`ReplayFrame`. Excluded from coverage per `M8-006c`; the frame itself is pinned by
`tests/unit/test_replay_view_model.py`.
"""

from __future__ import annotations

import tkinter as tk

from p2p_thief_agent.replay.view_model import ReplayFrame
from p2p_thief_agent.ui.style import ACCENT_WARM, INK, MUTED, PANEL, mix

OK_TEXT = "#34d399"
BAD_TEXT = "#f87171"
DETAIL_FIELDS = ("step", "sender", "move", "commit", "nonce", "verdict")


def build_detail(parent: tk.Frame, mono) -> dict[str, tk.Label]:
    """The step-under-cursor card: one labelled row per field the book names."""
    tk.Label(parent, text="STEP UNDER CURSOR", font=("Segoe UI", 8, "bold"),
             bg=PANEL, fg=ACCENT_WARM).grid(row=0, column=0, columnspan=2,
                                            sticky="w", padx=10, pady=8)
    labels: dict[str, tk.Label] = {}
    for index, name in enumerate(DETAIL_FIELDS, 1):
        tk.Label(parent, text=name, font=("Segoe UI", 8, "bold"), bg=PANEL,
                 fg=MUTED).grid(row=index, column=0, sticky="nw", padx=(10, 6), pady=2)
        value = tk.Label(parent, font=mono, bg=PANEL, fg=INK,
                         justify="left", wraplength=300)
        value.grid(row=index, column=1, sticky="w", padx=(0, 10), pady=2)
        labels[name] = value
    return labels


def paint_detail(labels: dict[str, tk.Label], frame: ReplayFrame) -> None:
    current = frame.current
    for name, value in zip(
        DETAIL_FIELDS,
        (current.step, current.sender, current.move, current.commit, current.nonce,
         current.reason),
        strict=True,
    ):
        labels[name].configure(text=value)


def paint_rows(rows: tk.Frame, frame: ReplayFrame, mono) -> None:
    """One line per record: verdict-coloured text, the cursor row lit in accent."""
    for child in rows.winfo_children():
        child.destroy()
    for row in frame.rows:
        text = (f"{'>' if row.is_current else ' '} step {row.step:>3}  {row.sender:<7}"
                f" {row.move:<4} {row.commit_short:<14} {row.verdict}")
        tk.Label(rows, text=text, font=mono, anchor="w",
                 bg=mix(PANEL, ACCENT_WARM, 0.12) if row.is_current else PANEL,
                 fg=OK_TEXT if row.ok else BAD_TEXT,
                 padx=10, pady=1).pack(fill="x")
