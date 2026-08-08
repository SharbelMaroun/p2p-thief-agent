"""Capture the replay screenshots the submission requires (`M8-015`, `M8-015b`, `M8-015d`).

The book calls this "absolute mandatory" in the README report (p.81/189): a screenshot
"from the replay application demonstrating Verified OK". Asked directly, **only**
`Verified OK` is mandatory — the `TAMPERED` capture is ours, because a viewer shown only
passing is a viewer that might not be checking anything.

**`M8-015d`: reproducible from committed inputs.** The condition is "a grader can
regenerate them", so the images are a function of JSON files committed in this repository
rather than artefacts of one session:

    uv run python scripts/capture_replay_screenshots.py

**The mandatory shot must show a real game, not a fixture (corrected 2026-08-08).** Asked
directly, the book requires the submission captures to show a game that was actually played
rather than a test fixture. So `Verified OK` is captured from `games/game-593df753457f/` --
the revealed log of a real two-process match this peer played, committed next to its
negotiated configuration. Until this correction the committed image showed a log that lived
only in a temporary directory: reproducible on one machine, on one day, by one person.

`TAMPERED` stays on the fixture deliberately. A forged log is not a game anyone played, so
there is no real version of it to photograph.

**These are real screen captures, not drawings.** The window is built, given a fixed size
so the output is stable, and photographed through the Windows GDI. A rendered picture of
what the app *would* look like would be a fabricated exhibit — the one thing a verification
screenshot must never be — so this goes through the real widget tree and fails loudly
rather than falling back to drawing anything.

Only the window's own rectangle is captured, never the whole desktop.
"""

from __future__ import annotations

import contextlib
import ctypes
import subprocess
import sys
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2p_thief_agent.replay import Replay, load_log  # noqa: E402
from p2p_thief_agent.ui.replay_app import ReplayWindow  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "replay"
PLAYED = ROOT / "games" / "game-593df753457f"
# `assets/` is the submission guidelines' conventional home for images. Asked directly, the
# book "only mandates that the images be displayed within the README.md academic report"
# and an `assets/` directory "is not mandated" — so this location is a project choice.
ASSETS = ROOT / "assets"
WINDOW = (1180, 520)
# (log, opponent log or None, image). The opponent's log is loaded for the played match so
# the board draws **both** trails, which is what the mutual audit actually looks at; a
# tampered fixture has no counterpart, so it draws one.
SHOTS = (
    (PLAYED / "log_game-593df753457f_g01.json",
     PLAYED / "log_game-593df753457f_g01.opponent.json",
     "replay-verified-ok.png"),
    (FIXTURES / "log_tampered.json", None, "replay-tampered.png"),
)

_CAPTURE = """
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap({w}, {h})
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen({x}, {y}, 0, 0, $bmp.Size)
$bmp.Save('{out}', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"""


def _match_screen_pixels() -> None:
    """Make Tk's coordinates mean physical pixels.

    Without this the capture comes out shifted — a strip of desktop down one edge and the
    title bar along the top — because Tk reports logical pixels while `CopyFromScreen`
    works in physical ones, so on a scaled display every `winfo_rootx` is wrong by the
    scale factor. Declaring the process DPI-aware makes them agree, which is what makes
    the output depend on the fixture rather than on the machine's display settings.
    """
    with contextlib.suppress(AttributeError, OSError):  # not Windows, or an older build
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]


def capture(window: tk.Misc, destination: Path) -> None:
    """Photograph exactly this window's rectangle through the Windows GDI."""
    window.update_idletasks()
    window.update()
    script = _CAPTURE.format(
        x=window.winfo_rootx(), y=window.winfo_rooty(),
        w=window.winfo_width(), h=window.winfo_height(),
        out=str(destination).replace("\\", "\\\\"),
    )
    subprocess.run(  # noqa: S603 - fixed command, interpolating only our own geometry
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        check=True, capture_output=True,
    )


def main() -> int:
    _match_screen_pixels()
    ASSETS.mkdir(exist_ok=True)
    for source, opponent_source, image in SHOTS:
        replay = Replay(load_log(source))
        opponent = load_log(opponent_source) if opponent_source else None
        window = ReplayWindow(replay, opponent=opponent)
        # Let Tk size the window to its own content. A fixed height cropped the transport
        # controls and the last rows of a 21-step match, so the picture proved less than the
        # viewer does -- the one failure mode a verification screenshot cannot have.
        window.root.update_idletasks()
        window.root.geometry("+80+80")
        if replay.verdict.first_bad is not None:
            replay.go_to_first_divergence()  # a TAMPERED shot must show the bad step
            window.refresh()
        else:
            while replay.position < replay.total - 1:  # end on the completed match
                replay.step_forward()
            window.refresh()
        window.root.update()
        destination = ASSETS / image
        capture(window.root, destination)
        window.root.destroy()
        size = destination.stat().st_size if destination.exists() else 0
        print(f"{image}: {replay.stamp.value}  ({size:,} bytes)")
        if not size:
            raise SystemExit(f"capture produced no file for {image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
