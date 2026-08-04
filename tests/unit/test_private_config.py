"""`M5-002f`: the opponent's address is private, and provably only private.

Two halves that only mean something together. The loader must read
`[network].opponent_url` from an explicit private path, and the shared match object
must be provably free of any network address -- without the second half, "private"
is a naming convention rather than a guarantee `[ADR-0004]`.
"""

from pathlib import Path

import pytest

from p2p_thief_agent.shared.private_config import (
    PrivateConfigError,
    SharedConfigLeakError,
    assert_no_network_address,
    load_opponent_url,
    load_private_config,
    opponent_url,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_TOML = ROOT / "config" / "thief" / "game.toml.example"

PRIVATE = """
[network]
my_port = 8801
opponent_url = "http://127.0.0.1:8802/mcp"
turn_timeout_seconds = 180
"""


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "game.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_the_opponent_url_comes_from_the_network_section(tmp_path: Path) -> None:
    assert load_opponent_url(write(tmp_path, PRIVATE)) == "http://127.0.0.1:8802/mcp"


def test_the_committed_example_parses_and_carries_the_expected_keys() -> None:
    """A stale example teaches the wrong shape to whoever fills the real file."""
    config = load_private_config(EXAMPLE_TOML)
    assert opponent_url(config).startswith("https://")
    assert set(config["network"]) >= {"my_port", "opponent_url", "turn_timeout_seconds"}


def test_a_missing_file_is_refused(tmp_path: Path) -> None:
    with pytest.raises(PrivateConfigError, match="cannot read"):
        load_opponent_url(tmp_path / "absent.toml")


def test_malformed_toml_is_refused(tmp_path: Path) -> None:
    with pytest.raises(PrivateConfigError, match="not valid TOML"):
        load_opponent_url(write(tmp_path, "[network\nopponent_url = "))


def test_a_missing_network_section_is_refused() -> None:
    with pytest.raises(PrivateConfigError, match=r"no \[network\] section"):
        opponent_url({"game": {"group_id": "thief-team"}})


@pytest.mark.parametrize("value", ["", "   ", 8802, None, ["http://x/mcp"]])
def test_an_empty_or_non_string_url_is_refused(value: object) -> None:
    with pytest.raises(PrivateConfigError, match="non-empty string"):
        opponent_url({"network": {"opponent_url": value}})


@pytest.mark.parametrize("value", ["127.0.0.1:8802", "ftp://host/mcp", "file:///etc/passwd"])
def test_an_undialable_scheme_is_refused(value: str) -> None:
    with pytest.raises(PrivateConfigError, match="must be http"):
        opponent_url({"network": {"opponent_url": value}})


# --- and nothing addressable may ride along in the shared object ---------------


def test_shared_timeouts_and_league_counts_are_not_addresses() -> None:
    """`network_and_league` is a legitimate shared block; only addresses are not."""
    assert_no_network_address(
        {"network_and_league": {"response_timeout_sec": 30, "num_games": 6}}
    )


def test_a_realistic_shared_match_object_passes() -> None:
    assert_no_network_address(
        {
            "board_and_agents": {"grid_size": 7, "thief_start": [3, 3]},
            "world": {"map_area": "New York", "hint_max_words": 15},
            "agreed_between": ["thief-team", "cop-team"],
        }
    )


@pytest.mark.parametrize(
    "shared",
    [
        {"network": {"opponent_url": "http://127.0.0.1:8802/mcp"}},
        {"board_and_agents": {"port": 8802}},
        {"identity": {"mcp_servers": ["http://a/mcp"]}},
        {"world": {"host": "127.0.0.1"}},
        {"deep": {"deeper": {"bind_port": 0}}},
    ],
)
def test_an_address_named_member_is_refused(shared: dict) -> None:
    with pytest.raises(SharedConfigLeakError, match="private network member"):
        assert_no_network_address(shared)


@pytest.mark.parametrize(
    "shared",
    [
        {"world": {"map_area": "https://example.invalid/mcp"}},
        {"extensions": {"notes": ["fine", "http://127.0.0.1:8802/mcp"]}},
        {"agreed_between": ["thief-team", "http://cop.invalid/mcp"]},
    ],
)
def test_an_address_valued_member_is_refused(shared: dict) -> None:
    """Renaming the key does not launder the value, so both checks are needed."""
    with pytest.raises(SharedConfigLeakError, match="network address"):
        assert_no_network_address(shared)
