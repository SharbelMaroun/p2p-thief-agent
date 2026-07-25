"""Tests for repository quality-gate helpers."""

from pathlib import Path

import pytest

from scripts import check_file_lengths, check_secrets, check_shared_contracts


def test_file_length_counters_distinguish_comments(tmp_path: Path) -> None:
    """Source limits ignore blank/comment-only lines; test limits remain physical."""
    sample = tmp_path / "sample.py"
    sample.write_text("# comment\n\nvalue = 1  # inline\n", encoding="utf-8")

    assert check_file_lengths.significant_line_count(sample) == 1
    assert check_file_lengths.physical_line_count(sample) == 3


def test_secret_scan_flags_fake_token_but_allows_dummy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Representative fake tokens fail without flagging documented dummy values."""
    fake_secret = "ghp_" + ("a" * 30)
    secret_file = tmp_path / "secret.txt"
    token_assignment = "TOKEN" + "=" + fake_secret
    secret_file.write_text(f"{token_assignment}\n", encoding="utf-8")
    dummy_file = tmp_path / "dummy.env"
    dummy_file.write_text("API_KEY=dummy-provider-key\n", encoding="utf-8")
    bypass_file = tmp_path / "bypass.env"
    password_line = "PASSWORD" + "=" + "real-" + "example-secret"
    token_line = "TOKEN" + "=" + "not-a-" + "placeholder"
    bypass_file.write_text(f"{password_line}\n{token_line}\n", encoding="utf-8")
    monkeypatch.setattr(check_secrets, "PROJECT_ROOT", tmp_path)

    assert check_secrets.findings(secret_file)
    assert check_secrets.findings(dummy_file) == []
    assert len(check_secrets.findings(bypass_file)) == 2


def test_contract_check_fails_closed(capsys: pytest.CaptureFixture[str]) -> None:
    """No unavailable Cop proposal can be reported as a passing parity check."""
    assert check_shared_contracts.main() == 1
    assert "PENDING" in capsys.readouterr().out
