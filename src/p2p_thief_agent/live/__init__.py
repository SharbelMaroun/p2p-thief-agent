"""The live GUI's data layer: local truth, and the screen derived from it.

Rule 8 (Mandatory): "Display true local information only in the live user interface.
Sanction: Disqualification due to data breach." Rule 9 (Prohibited): "Do not display the
full objective board state in the live user interface. Sanction: **Project
disqualification** due to unfair advantage."

* `local_truth` — the closed set of things the screen may know, built from explicit
  arguments so the opponent's real position has nowhere to sit.
* `view_model` — that snapshot projected onto cells, colours, marks and a banner.

The widgets are in `ui/live_app.py` and read `LiveFrame` only. This is the Thief's screen:
our marker is `T`, and the inference we draw is about the police (`C?`).
"""

from p2p_thief_agent.live.local_truth import Cell, Grid, LocalTruth, TurnState, local_truth
from p2p_thief_agent.live.view_model import CellView, LiveFrame, frame_of, heat_colour

__all__ = [
    "Cell",
    "CellView",
    "Grid",
    "LiveFrame",
    "LocalTruth",
    "TurnState",
    "frame_of",
    "heat_colour",
    "local_truth",
]
