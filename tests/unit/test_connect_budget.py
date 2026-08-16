"""The connect wait comes from private config, not `serve_match`'s default.

Found live in the first amireman smoke (2026-08-13): game 1 finished, their Police
server was still rebinding for sub-game 2, and our Thief gave up after the hardcoded
30 seconds even though both private TOMLs say ``connect_timeout_seconds = 600``.
The Cop has honoured the key since M9; this pins the Thief's side of the symmetry.
"""

from pathlib import Path

from p2p_thief_agent.adapters.play_command import _connect_budget
from p2p_thief_agent.services.readiness import DEFAULT_CONNECT_TIMEOUT


def test_the_private_budget_is_honoured(tmp_path: Path) -> None:
    private = tmp_path / "game.toml"
    private.write_text("[network]\nconnect_timeout_seconds = 600\n", encoding="utf-8")
    assert _connect_budget(private) == 600.0


def test_no_private_file_falls_back(tmp_path: Path) -> None:
    assert _connect_budget(None) == DEFAULT_CONNECT_TIMEOUT
    assert _connect_budget(tmp_path / "missing.toml") == DEFAULT_CONNECT_TIMEOUT


def test_our_shipped_config_outwaits_the_opponent_without_stalling_the_series() -> None:
    """The real file the series runs with: a regression here ends a live match.

    Was ``== 600.0`` ("ten minutes") until 2026-08-16. The guard is not about that number
    -- it exists so the key cannot silently revert to the 30s default mid-series -- so it
    now pins the property the value is chosen for, and both bounds have a live failure
    behind them:

    * **above the opponent's patience.** yanell11 wait 300s for the first handshake and
      180s per sub-game; the amireman smoke lost a sub-game to a 30s give-up while their
      Police was still rebinding. Quitting before the peer stops trying loses a game we
      would have played.
    * **below a stall that eats the session.** Run 5 sub-game 2 sat the full 600s dialling
      a dead host after yanell11 had given up at 180s. One lost sub-game became a lost
      series because nothing was left of the window to diagnose and restart.
    """
    budget = _connect_budget(Path("config/thief/game.toml"))
    assert budget != DEFAULT_CONNECT_TIMEOUT, "the private key stopped being read"
    assert 180.0 < budget <= 300.0, f"{budget}s is outside the agreed handshake window"
