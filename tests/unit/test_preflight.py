"""`M9-038`: the readout must be able to say NOT ready, or it is decoration.

Every check below is driven to **both** verdicts. A preflight that only ever prints green is
the same failure as the `[email] mode = "draft"` key this command replaced: something that
looks like a control and reports nothing.
"""

from __future__ import annotations

import json
import socket
import tomllib
from pathlib import Path

from p2p_thief_agent.services.preflight import ARMED, DISABLED, preflight

ROOT = Path(__file__).resolve().parents[2]
MATCH = ROOT / "config" / "match_amireman.json"
EXAMPLE_TOML = ROOT / "config" / "thief" / "game.toml.example"


def _named(checks, name):
    return next(check for check in checks if check.name == name)


def _private(tmp_path: Path, *, port: int = 8899, credential: str = "C:/nowhere/token.json",
             group_id: str = "sharNamr") -> Path:
    """`group_id` defaults to a real participant of `MATCH`. It used to be `"t"`, which was
    fine while nothing compared it to anything; `participants` compares it to
    `agreed_between`, so a placeholder now reads as "not our match" -- tested below."""
    path = tmp_path / "game.toml"
    path.write_text(
        'version = "1.00"\n'
        f'[game]\ngroup_name = "t"\ngroup_id = "{group_id}"\nsub_game_number = 1\n'
        'members = ["t"]\n'
        'repos = { cop = "https://example.invalid/c", thief = "https://example.invalid/t" }\n'
        f'[network]\nmy_port = {port}\nopponent_url = "https://them.invalid/mcp"\n'
        'public_url = "https://us.invalid/mcp"\nturn_timeout_seconds = 180\n'
        'poll_interval_seconds = 1\nconnect_timeout_seconds = 120\nretry_interval_seconds = 5\n'
        'audit_send_timeout_seconds = 60\n'
        '[strategy]\nname = "t"\n[llm]\nmodel = "t"\nstep_deadline_seconds = 30\n'
        '[hardware]\nos = ""\ncpu_type = ""\ncpu_freq_mhz = 1\ncpu_cores = 1\nram_gb = 1\n'
        'gpu_model = "none"\nvram_gb = 0\n'
        f'[reporting]\ncredential_path = "{credential}"\n',
        encoding="utf-8")
    return path


def test_a_configured_peer_reports_ready(tmp_path: Path) -> None:
    checks = preflight(MATCH, _private(tmp_path))
    assert not [check.name for check in checks if check.failed]
    assert _named(checks, "match config").ok is True


def test_reporting_is_disabled_when_no_credential_exists(tmp_path: Path) -> None:
    """**The question this command was built to answer.** No credential = cannot send."""
    assert DISABLED in _named(preflight(MATCH, _private(tmp_path)), "reporting").value


def test_a_present_credential_is_reported_as_armed_and_fails(tmp_path: Path) -> None:
    """The inverse case, which is what makes the DISABLED line mean anything.

    An armed sender is the *surprising* state before a friendly series, so it is a failure
    rather than a quiet note -- the operator should have to look at it.
    """
    credential = tmp_path / "token.json"
    credential.write_text("{}", encoding="utf-8")
    check = _named(preflight(MATCH, _private(tmp_path, credential=credential.as_posix())),
                   "reporting")
    assert ARMED in check.value
    assert check.failed


def test_an_occupied_port_is_reported_rather_than_discovered_mid_match(tmp_path: Path) -> None:
    """The reference runs this check for a reason: a stale peer holding the port surfaces
    as `WinError 10048` at startup, or worse, as the *opponent* appearing absent."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as held:
        held.bind(("127.0.0.1", 0))
        held.listen(1)
        port = held.getsockname()[1]
        check = _named(preflight(MATCH, _private(tmp_path, port=port)), "port")
        assert check.failed
        assert "IN USE" in check.value


def test_a_match_config_breaking_appendix_f_fails(tmp_path: Path) -> None:
    """Rule 12: a lowered Minimum must stop the match here, not at an audit."""
    game = json.loads(MATCH.read_text(encoding="utf-8"))
    game["board_and_agents"]["grid_size"] = 5  # below the Appendix F floor of 7
    broken = tmp_path / "bad_match.json"
    broken.write_text(json.dumps(game), encoding="utf-8")
    check = _named(preflight(broken, _private(tmp_path)), "match config")
    assert check.failed
    assert "board_size" in check.value


def test_a_match_naming_roles_instead_of_groups_fails(tmp_path: Path) -> None:
    """The uoh-ay26 defect, 2026-08-11: `agreed_between` held the two *roles*.

    Everything else about that file was legal -- 14 terms, Appendix F clean -- so this
    command printed `ready` for a match the handshake then refused before move one.
    """
    game = json.loads(MATCH.read_text(encoding="utf-8"))
    game["agreed_between"] = ["cop", "thief"]
    broken = tmp_path / "roles_match.json"
    broken.write_text(json.dumps(game), encoding="utf-8")
    check = _named(preflight(broken, _private(tmp_path)), "participants")
    assert check.failed
    assert "sharNamr" in check.value


def test_a_match_we_are_not_a_party_to_fails(tmp_path: Path) -> None:
    """Two named groups, both real, neither of them us -- still not our match."""
    check = _named(preflight(MATCH, _private(tmp_path, group_id="someone-else")), "participants")
    assert check.failed


def test_an_unsupported_schema_version_fails(tmp_path: Path) -> None:
    """`ADR-0003`: uoh-ay26 sent `"1.00"`, the reference ships `"1.3"`, Appendix B says `"1.2"`.

    Three sources, three values, so an unimplemented one is refused rather than guessed.
    """
    game = json.loads(MATCH.read_text(encoding="utf-8"))
    game["schema_version"] = "1.00"
    broken = tmp_path / "old_schema.json"
    broken.write_text(json.dumps(game), encoding="utf-8")
    check = _named(preflight(broken, _private(tmp_path)), "schema version")
    assert check.failed
    assert "1.00" in check.value


def test_an_unreadable_private_config_is_reported_not_raised(tmp_path: Path) -> None:
    """A readout that crashes tells the operator less than one that says what is wrong."""
    checks = preflight(MATCH, tmp_path / "absent.toml")
    assert _named(checks, "private config").failed


def test_the_example_config_carries_no_dead_email_toggle() -> None:
    """**Removed 2026-08-08.** `[email] mode = "draft"` sat here and no code ever read it.

    A switch wired to nothing is worse than no switch: it invites someone to believe
    reporting is off because a file says `draft`, when what actually stops a send is the
    absence of a credential.

    Checked against the parsed document, not the raw text: the template *explains* the
    removal in a comment, and a test that matched prose would fail on its own rationale.
    """
    parsed = tomllib.loads(EXAMPLE_TOML.read_text(encoding="utf-8"))
    assert "email" not in parsed
    assert "mode" not in parsed.get("reporting", {})
