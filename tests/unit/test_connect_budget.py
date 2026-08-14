"""The connect wait comes from private config, not `serve_match`'s default.

Found live in the first amireman smoke (2026-08-13): game 1 finished, their Police
server was still rebinding for sub-game 2, and our Thief gave up after the hardcoded
30 seconds even though both private TOMLs say ``connect_timeout_seconds = 600``.
The Cop has honoured the key since M9; this pins the Thief's side of the symmetry.
"""

from pathlib import Path

import pytest

from p2p_thief_agent.adapters.play_command import _connect_budget
from p2p_thief_agent.services.readiness import DEFAULT_CONNECT_TIMEOUT

_SHIPPED_PRIVATE = Path("config/thief/game.toml")


def test_the_private_budget_is_honoured(tmp_path: Path) -> None:
    private = tmp_path / "game.toml"
    private.write_text("[network]\nconnect_timeout_seconds = 600\n", encoding="utf-8")
    assert _connect_budget(private) == 600.0


def test_no_private_file_falls_back(tmp_path: Path) -> None:
    assert _connect_budget(None) == DEFAULT_CONNECT_TIMEOUT
    assert _connect_budget(tmp_path / "missing.toml") == DEFAULT_CONNECT_TIMEOUT


def test_our_shipped_config_asks_for_ten_minutes() -> None:
    """The real file the series runs with: a regression here ends a live match.

    This asserts a property of the operator's **private** `config/thief/game.toml`, which is
    gitignored (never committed — see `docs/MATCH_RUNBOOK.md`) and so is absent from any clean
    clone or CI runner. When it is absent there is nothing to check and the test skips rather
    than failing on a file that was deliberately kept out of version control; when an operator
    does have it, the 600-second budget is asserted exactly as before.
    """
    if not _SHIPPED_PRIVATE.exists():
        pytest.skip("private config/thief/game.toml is absent (gitignored, operator-only)")
    assert _connect_budget(_SHIPPED_PRIVATE) == 600.0
