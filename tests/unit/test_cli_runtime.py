"""`M9-025`: the agent can be driven from a terminal.

Until 2026-08-07 this CLI was a scaffold whose own description said "no peer runtime is
implemented". Everything underneath was finished and exercised; a grader who cloned the
repository still could not start anything. These tests hold the wiring in place.

Two properties get most of the attention, because both fail silently:

* **`build_parser` imports no transport.** `--version` on a machine without FastMCP must
  answer, not traceback. A runtime import that drifts to module scope breaks that, and
  nothing else in the suite would notice — every other test has the dependency installed.
* **`verify` exits non-zero on a tampered log.** A gate that prints `TAMPERED` and returns 0
  is worse than no gate: a pipeline reads the exit code, not the prose.
"""

from __future__ import annotations

import ast
import json
import pathlib

import pytest

from p2p_thief_agent.cli import build_parser, main

CLI_SOURCE = pathlib.Path(
    __import__("p2p_thief_agent.cli", fromlist=["__file__"]).__file__)
RECORD = {"payload": {"step": 1, "move": "N"}, "nonce": "n" * 32}


def written_log(tmp_path: pathlib.Path, *, tamper: bool = False) -> pathlib.Path:
    """A real commit-reveal log on disk, optionally with one reveal rewritten."""
    from p2p_thief_agent.protocol.crypto import commit_of

    records = []
    for step in (1, 2):
        payload = {"step": step, "move": "NE"[step % 2]}
        nonce = f"{step:032x}"
        commit = commit_of(payload, nonce)
        if tamper and step == 2:
            payload = {**payload, "move": "S"}
        records.append({"payload": payload, "nonce": nonce, "commit": commit})
    path = tmp_path / "log_demo_g01.json"
    path.write_text(json.dumps({"records": records}, indent=2), encoding="utf-8")
    return path


# --- the parser must not need a transport ------------------------------------------------


def test_the_parser_imports_nothing_from_the_transport_layer() -> None:
    """**The property that breaks silently.** Every other test has FastMCP installed, so a
    runtime import drifting to module scope would go unnoticed until a grader without it
    ran `--version` and got a traceback about something they never asked for."""
    tree = ast.parse(CLI_SOURCE.read_text(encoding="utf-8"))
    module_level = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
    for node in module_level:
        assert node.module and "adapters" not in node.module, (
            f"cli.py imports {node.module} at module scope; --version must work without a "
            "transport installed")


def test_help_and_version_need_no_subcommand() -> None:
    parser = build_parser()
    assert parser.prog == "p2p-thief"
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args(["--version"])
    assert exit_info.value.code == 0


def test_no_subcommand_prints_help_and_succeeds(capsys) -> None:
    """A bare invocation is a question, not an error."""
    assert main([]) == 0
    assert "serve" in capsys.readouterr().out


@pytest.mark.parametrize("command", ["serve", "replay", "verify"])
def test_every_advertised_subcommand_parses(command: str) -> None:
    extra = [] if command == "serve" else ["--log", "x.json"]
    assert build_parser().parse_args([command, *extra]).command == command


# --- replay and verify: rule 20 from a terminal --------------------------------------------


def test_replay_prints_the_banner_for_a_clean_log(tmp_path, capsys) -> None:
    """The banner is the text the mandatory screenshot shows (p.81/189), so it is evidence
    rather than a debug line."""
    assert main(["replay", "--log", str(written_log(tmp_path))]) == 0
    assert "Verified OK" in capsys.readouterr().out


def test_verify_is_silent_but_still_succeeds(tmp_path, capsys) -> None:
    assert main(["verify", "--log", str(written_log(tmp_path))]) == 0
    assert capsys.readouterr().out == ""


def test_verify_exits_non_zero_on_a_tampered_log(tmp_path) -> None:
    """**A gate that prints TAMPERED and returns 0 is worse than no gate** — a pipeline
    reads the exit code, not the prose."""
    assert main(["verify", "--log", str(written_log(tmp_path, tamper=True))]) == 1


def test_replay_reports_a_tampered_log_and_exits_non_zero(tmp_path, capsys) -> None:
    assert main(["replay", "--log", str(written_log(tmp_path, tamper=True))]) == 1
    assert "TAMPERED" in capsys.readouterr().out.upper()


def test_a_missing_log_exits_two_rather_than_tracebacking(tmp_path, capsys) -> None:
    """Exit 2 separates "could not read it" from "read it and it failed" — an operator
    seeing 1 should reach for the evidence, not for the path."""
    assert main(["replay", "--log", str(tmp_path / "absent.json")]) == 2
    assert "could not read" in capsys.readouterr().out


def test_an_unreadable_log_is_refused_without_accusing_anyone(tmp_path, capsys) -> None:
    """A malformed file is not a forgery. Saying so matters because rule 19's sanction
    lands on whoever is accused."""
    broken = tmp_path / "log_broken.json"
    broken.write_text("{not json", encoding="utf-8")
    assert main(["replay", "--log", str(broken)]) == 2
    assert "TAMPERED" not in capsys.readouterr().out.upper()
