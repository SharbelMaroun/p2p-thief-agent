"""The replay window (`M8-002`, `M8-002e`) — widgets only, no logic.

Rule 20 is Mandatory with the sanction "threshold condition for confirmation of logs and
submission of the project" (p.129/272). `replay/` satisfies the verification; this file
satisfies the *app*, and produces the `Verified OK` capture the book calls "absolute
mandatory" in the README report (p.81/189).

**What the screen shows**, asked directly: the `nonce`, `move` and original `commit` from
the log entry (p.56/142); a clear verdict indicator — green `Verified OK` or a bright red
`TAMPERED` banner; and controls to move "back and forth in time" (p.56/141). **The board
is drawn as well (`M8-016`)**: the replay runs in the audit phase as the book's
"Retrospective Witness" (p.54/135) — rule 9's objective-board ban binds the live interface
only — and the reference viewer itself paints both true positions on one board when the
opponent's log sits beside our own, falling back to a single trail when it is not. `Play`
auto-advances the cursor; the banner remains the mandatory screenshot, its green/red
semantic and pinned — only the chrome is styling. The belief map stays live-side (`M8-015a`).

**Every widget reads `ReplayFrame` and nothing else** (`M8-006`). Excluded from coverage
by `M8-006c`; the screen's claims are pinned by the view-model and board tests.

Controls follow the reference's set — restart, back, step, play — plus **jump to the
first divergence**, because the only question a decided match leaves open is which step.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

from p2p_thief_agent.replay.board import board_frame
from p2p_thief_agent.replay.cursor import Replay
from p2p_thief_agent.replay.load import ReplayLog
from p2p_thief_agent.replay.view_model import frame_of
from p2p_thief_agent.ui.replay_board import paint_board
from p2p_thief_agent.ui.replay_panels import (
    BAD_TEXT,
    build_detail,
    paint_detail,
    paint_rows,
)
from p2p_thief_agent.ui.style import (
    BG,
    INK,
    MUTED,
    PANEL,
    PANEL_EDGE,
    apply_icon,
    banner_pill,
    style_button,
)

_ICON = Path(__file__).resolve().parents[3] / "assets" / "icon.png"
BANNER_W, BANNER_H = 1200, 58


class ReplayWindow:
    """A Tk window over a `Replay`. Holds widgets; derives every string from the frame."""

    def __init__(self, replay: Replay, root: tk.Misc | None = None,
                 opponent: ReplayLog | None = None) -> None:
        self._replay = replay
        self._opponent = opponent
        self._captured = "capture" in str(replay.log.document.get("summary", "")).lower()
        self._playing = False
        self.root = root or tk.Tk()
        self.root.title("Replay Viewer — cryptographic verification")
        self.root.configure(bg=BG)
        self._icon = apply_icon(self.root, _ICON)
        self._mono = tkfont.Font(family="Consolas", size=9)
        self._build()
        self.refresh()

    # --- widgets ------------------------------------------------------------------------

    def _build(self) -> None:
        self._stamp = tk.Canvas(self.root, width=BANNER_W, height=BANNER_H,
                                bg=BG, highlightthickness=0)
        self._stamp.pack(fill="x", padx=10, pady=(10, 0))
        self._source = tk.Label(self.root, font=("Segoe UI", 8), bg=BG, fg=MUTED)
        self._source.pack(fill="x")
        self._sequence = tk.Label(self.root, font=("Segoe UI", 8), bg=BG)
        self._sequence.pack(fill="x", pady=(0, 6))

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=12)
        board_panel = tk.Frame(body, bg=PANEL, highlightthickness=1,
                               highlightbackground=PANEL_EDGE)
        board_panel.pack(side="left", fill="y")
        self._board = tk.Canvas(board_panel, highlightthickness=0)
        self._board.pack(padx=8, pady=8)
        self._board_caption = tk.Label(board_panel, font=("Segoe UI", 8), bg=PANEL,
                                       fg=MUTED)
        self._board_caption.pack(fill="x", pady=(0, 8))
        self._rows = tk.Frame(body, bg=PANEL, highlightthickness=1,
                              highlightbackground=PANEL_EDGE)
        self._rows.pack(side="left", fill="both", expand=True, padx=(12, 0))
        detail = tk.Frame(body, bg=PANEL, highlightthickness=1,
                          highlightbackground=PANEL_EDGE)
        detail.pack(side="left", fill="both", padx=(12, 0))
        self._detail = build_detail(detail, self._mono)
        self._build_controls()

    def _build_controls(self) -> None:
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=12, pady=10)
        for text, command in (
            ("|< Restart", self._replay.restart),
            ("< Back", self._replay.step_back),
            ("Step >", self._replay.step_forward),
            ("Jump to divergence", self._replay.go_to_first_divergence),
        ):
            button = tk.Button(bar, text=text, font=("Segoe UI", 9), width=16,
                               command=self._act(command))
            style_button(button)
            button.pack(side="left", padx=4)
        self._play = tk.Button(bar, text="Play", font=("Segoe UI", 9), width=8,
                               command=self._toggle_play)
        style_button(self._play)
        self._play.pack(side="left", padx=4)
        self._position = tk.Label(bar, font=("Segoe UI", 9, "bold"), bg=BG, fg=INK)
        self._position.pack(side="right")

    def _toggle_play(self) -> None:
        """Auto-advance the cursor; stop at the last step or on `Pause` (`M8-016`)."""
        self._playing = not self._playing
        self._play.configure(text="Pause" if self._playing else "Play")
        if self._playing:
            self._tick()

    def _tick(self) -> None:
        if not self._playing:
            return
        if self._replay.position >= self._replay.total - 1:
            self._toggle_play()
            return
        self._replay.step_forward()
        self.refresh()
        self.root.after(500, self._tick)

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
        width = max(BANNER_W, self.root.winfo_width())
        banner_pill(self._stamp, width, BANNER_H, frame.stamp_colour,
                    frame.stamp, frame.banner)
        self._source.configure(text=f"{frame.origin}   ·   game {frame.game_id}"
                                    f"   ·   sub-game {frame.sub_game}")
        self._sequence.configure(text=frame.sequence_summary,
                                 fg=MUTED if frame.sequence_ok else BAD_TEXT)
        self._position.configure(text=frame.position_label)
        board = board_frame(self._replay.log, self._replay.position,
                            opponent=self._opponent, captured=self._captured)
        paint_board(self._board, board)
        self._board_caption.configure(text=board.caption)
        paint_rows(self._rows, frame, self._mono)
        paint_detail(self._detail, frame)


def run(replay: Replay, opponent: ReplayLog | None = None) -> None:  # pragma: no cover
    ReplayWindow(replay, opponent=opponent).root.mainloop()
