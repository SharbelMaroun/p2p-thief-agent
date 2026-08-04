"""`M5-006`: the Thief runs under its own role-scoped config directory.

Two peers on one machine must not share private configuration — separate `config/police/`
and `config/thief/` directories are how the book keeps each peer's port, opponent URL, and
model choice its own business. The resolver is scoped to `thief/` by construction, so this
peer cannot read the police directory even by mistake `[AE-1]` `[AE-2]`.
"""

from pathlib import Path

import pytest

from p2p_thief_agent.shared.private_config import (
    THIEF_ROLE,
    PrivateConfigError,
    load_thief_private_config,
    thief_config_path,
)

ROOT = Path(__file__).resolve().parents[2]

GAME_TOML = """
[network]
my_port = 8801
opponent_url = "http://127.0.0.1:8802/mcp"
turn_timeout_seconds = 180
"""


def test_the_resolver_targets_the_thiefs_own_role_directory(tmp_path: Path) -> None:
    path = thief_config_path(tmp_path)
    assert path == tmp_path / "thief" / "game.toml"
    # Role-scoped by construction: the police directory is never on this path.
    assert THIEF_ROLE in path.parts
    assert "police" not in path.parts


def test_it_loads_the_private_toml_from_the_thief_directory(tmp_path: Path) -> None:
    thief_dir = tmp_path / "thief"
    thief_dir.mkdir()
    (thief_dir / "game.toml").write_text(GAME_TOML, encoding="utf-8")

    config = load_thief_private_config(tmp_path)
    assert config["network"]["opponent_url"] == "http://127.0.0.1:8802/mcp"


def test_a_police_sibling_file_is_not_read_by_the_thief(tmp_path: Path) -> None:
    """The Thief resolver ignores a police `game.toml` sitting right beside it."""
    (tmp_path / "police").mkdir()
    (tmp_path / "police" / "game.toml").write_text(GAME_TOML, encoding="utf-8")
    # The thief directory is absent, so loading fails rather than silently reading police.
    with pytest.raises(PrivateConfigError):
        load_thief_private_config(tmp_path)


def test_the_committed_skeleton_lives_in_the_thief_role_directory() -> None:
    assert (ROOT / "config" / "thief" / "game.toml.example").is_file()
    assert not (ROOT / "config" / "game.toml.example").exists()
