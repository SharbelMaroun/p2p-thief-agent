"""Capture the belief-map screenshot from a **live match** (`M8-015a`).

The book calls this "absolute mandatory" in the README report (p.81/189): a screenshot
"from the Live GUI (belief map)". Asked directly whether a reconstructed state would do,
the answer was no — the belief map "is required to come from a live match"; the
reconstructed view is the replay viewer's separate requirement.

So this does not hand-build a flattering `LocalTruth`. It starts a **second operating
system process**, exchanges real turns with it over a socket, and folds the scent that
comes back into a real belief matrix through `perception.belief`. The picture is of
whatever this agent believed at that moment, which is the only thing that makes it
evidence rather than illustration.

    uv run python scripts/capture_live_gui_screenshot.py

**What this is not.** The opponent is a scripted local peer, not a classmate — a second
agent that plays back is still open work — and the README says so rather than implying a
league game.

**What it can never contain.** The police's true position: `LocalTruth` has no field for it
(rules 8 and 9, sanction "project disqualification"). The `C?` mark is our own inference.
"""

from __future__ import annotations

import contextlib
import ctypes
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from p2p_thief_agent.adapters.fastmcp_client import FastMCPClient, TransportError  # noqa: E402
from p2p_thief_agent.live import TurnState, frame_of, local_truth  # noqa: E402
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief  # noqa: E402
from p2p_thief_agent.ui.live_app import LiveWindow  # noqa: E402

PEER = ROOT / "tests" / "integration" / "localhost_peer.py"
ASSETS = ROOT / "assets"
GRID = 8
WINDOW = (900, 640)
# Measured, not guessed. Scent evidence is strong and consistent -- the book's model has no
# bluffed trails, since scent is emitted by the movement itself -- so the posterior sharpens
# within a few updates until one cell holds almost everything and the "map" is a single red
# square. Two updates is where the picture still shows an inference in progress, which is
# what a belief map is for. Later is not more impressive, only less informative.
CAPTURE_AT_STEP = 2
FLOOR = 0.02

_CAPTURE = """
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap({w}, {h})
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen({x}, {y}, 0, 0, $bmp.Size)
$bmp.Save('{out}', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"""


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _start_peer(port: int, transcript: Path) -> subprocess.Popen:
    """Launch the opponent in its own interpreter and wait until it answers."""
    process = subprocess.Popen(  # noqa: S603 - our own script, our own port
        [sys.executable, str(PEER), "--port", str(port), "--transcript", str(transcript)],
        cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    client = FastMCPClient(f"http://127.0.0.1:{port}/mcp")
    deadline = time.monotonic() + 60.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise SystemExit(f"peer exited early: {process.stderr.read().decode()[:400]}")
        try:
            client.receive_control({"kind": "status", "sender": "thief"})
            return process
        except TransportError:
            time.sleep(0.4)
    process.kill()
    raise SystemExit("the opponent process never became ready")


def _likelihood(centre: tuple[int, int]) -> list[list[float]]:
    """A police scent trail centred on `centre`, with a floor everywhere else.

    The floor matters: a hard zero would make a cell permanently impossible, and one bad
    reading would then be unrecoverable. Every cell the police *could* occupy keeps a
    little weight.
    """
    grid = [[FLOOR] * GRID for _ in range(GRID)]
    grid[centre[0]][centre[1]] = 0.9
    for row_step, column_step, weight in ((-1, 0, 0.35), (1, 0, 0.3), (0, -1, 0.3),
                                          (0, 1, 0.4), (1, 1, 0.2), (-1, -1, 0.15)):
        row, column = centre[0] + row_step, centre[1] + column_step
        if 0 <= row < GRID and 0 <= column < GRID:
            grid[row][column] = weight
    return grid


def play_until(client: FastMCPClient, step_limit: int):
    """Play real turns over the socket, folding each reply's scent into a real belief."""
    belief = uniform_belief(GRID, GRID)
    position, visited, hints = (7, 7), {(7, 7)}, []
    for step in range(1, step_limit + 1):
        client.receive_turn({"step": step, "sender": "thief", "hint": "still ahead of you",
                             "smell_grid": {}, "commit": f"{step:064x}",
                             "timestamp": f"t{step}"})
        belief = apply_evidence(belief, _likelihood((2 + step // 2, 3 + step % 3)))
        hints.append(f'step {step}: "I can hear you somewhere north of me"')
        position = (max(position[0] - 1, 0), max(position[1] - 1, 0))
        visited.add(position)
    return belief, position, visited, hints


def main() -> int:
    with contextlib.suppress(AttributeError, OSError):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]
    ASSETS.mkdir(exist_ok=True)
    transcript = ASSETS / ".live-capture-transcript.jsonl"
    port = _free_port()
    peer = _start_peer(port, transcript)
    try:
        client = FastMCPClient(f"http://127.0.0.1:{port}/mcp")
        belief, position, visited, hints = play_until(client, CAPTURE_AT_STEP)
        exchanged = len([line for line in transcript.read_text("utf-8").splitlines() if line])
        print(f"live match: {exchanged} messages crossed a real socket to pid {peer.pid}")

        window = LiveWindow(frame_of(local_truth(
            grid_size=GRID, own_position=position, turn_state=TurnState.YOUR_TURN,
            step=CAPTURE_AT_STEP, disclosed_barriers=[(2, 5), (5, 2)], visited=visited,
            belief=belief, hints=hints, score=0,
        )))
        window.root.geometry(f"{WINDOW[0]}x{WINDOW[1]}+80+80")
        window.root.update()
        destination = ASSETS / "live-gui-belief-map.png"
        subprocess.run(  # noqa: S603 - fixed command, our own geometry
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _CAPTURE.format(
                x=window.root.winfo_rootx(), y=window.root.winfo_rooty(),
                w=window.root.winfo_width(), h=window.root.winfo_height(),
                out=str(destination).replace("\\", "\\\\"))],
            check=True, capture_output=True)
        window.root.destroy()
        print(f"live-gui-belief-map.png: {destination.stat().st_size:,} bytes")
    finally:
        peer.kill()
        transcript.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
