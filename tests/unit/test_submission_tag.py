"""`M9-019`: the submission tag names the reviewed commit, not a later one.

Rule 41 wants an annotated `v1.0-submission` tag on the accepted submission commit, "not at a
later commit written after the deadline". The failure is ordinary: you tag, then fix one more
thing, then push. The tag still exists and the repository still looks tidy — it simply names a
commit nobody reviewed.

**These tests were rewritten on 2026-08-08, and the old ones are why.** They ran the checker
against *this* repository and asserted `main() in (0, 1)` — true of any function returning an
int — plus `isinstance(tag_exists(), bool)`. Worse, one returned early the moment a tag
existed, so the suite went quiet at exactly the point the "tag names an older commit" failure
becomes possible. A test that cannot fail is not evidence, and a test that switches itself off
when the risk appears is worse than none.

Every case below builds a **real throwaway Git repository** and drives the checker at it, so
each branch of `main()` is exercised deterministically instead of depending on whatever state
this working tree happens to be in.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.check_submission_tag import (
    TAG,
    commits_after,
    is_annotated,
    main,
    tag_exists,
)


def _run(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _repo(tmp_path: Path) -> Path:
    """A throwaway repository with one commit and an identity, so tagging works."""
    _run("init", "-q", "-b", "main", cwd=tmp_path)
    _run("config", "user.email", "test@example.invalid", cwd=tmp_path)
    _run("config", "user.name", "Test", cwd=tmp_path)
    (tmp_path / "file.txt").write_text("one\n", encoding="utf-8")
    _run("add", "file.txt", cwd=tmp_path)
    _run("commit", "-qm", "first", cwd=tmp_path)
    return tmp_path


def _commit(repo: Path, text: str) -> None:
    (repo / "file.txt").write_text(text, encoding="utf-8")
    _run("commit", "-qam", text, cwd=repo)


def test_the_tag_name_is_the_one_rule_41_asks_for() -> None:
    assert TAG == "v1.0-submission"


def test_an_untagged_repository_fails_and_prints_the_command_to_fix_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """The state a repository is in until submission: a useful answer, not a traceback."""
    monkeypatch.chdir(_repo(tmp_path))
    assert main() == 1
    output = capsys.readouterr().out
    assert "git tag -a" in output and TAG in output


def test_a_correctly_tagged_repository_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """**The case the old tests could not reach.** Annotated, current, clean — exit 0."""
    repo = _repo(tmp_path)
    monkeypatch.chdir(repo)
    _run("tag", "-a", TAG, "-m", "submission", cwd=repo)
    assert tag_exists() and is_annotated() and commits_after() == []
    assert main() == 0
    assert "OK" in capsys.readouterr().out


def test_a_lightweight_tag_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Rule 41 asks for provenance, which only an annotated tag carries."""
    repo = _repo(tmp_path)
    monkeypatch.chdir(repo)
    _run("tag", TAG, cwd=repo)
    assert tag_exists() and not is_annotated()
    assert main() == 1
    assert "lightweight" in capsys.readouterr().out


def test_a_commit_made_after_the_tag_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """**The failure this module exists for**: tag, then fix one more thing. The tag now
    names a commit nobody reviewed, and nothing about the repository looks wrong."""
    repo = _repo(tmp_path)
    monkeypatch.chdir(repo)
    _run("tag", "-a", TAG, "-m", "submission", cwd=repo)
    _commit(repo, "two")
    assert len(commits_after()) == 1
    assert main() == 1
    assert "after" in capsys.readouterr().out


def test_an_uncommitted_change_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """A tag names a commit, and a commit cannot contain work that was never committed."""
    repo = _repo(tmp_path)
    monkeypatch.chdir(repo)
    _run("tag", "-a", TAG, "-m", "submission", cwd=repo)
    (repo / "file.txt").write_text("uncommitted\n", encoding="utf-8")
    assert main() == 1
    assert "uncommitted" in capsys.readouterr().out


def test_a_nonexistent_tag_reports_no_later_commits_rather_than_erroring(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`rev-list absent..HEAD` fails; returning an empty list keeps the *reason* for failure
    with the tag-exists check, where the message can explain it."""
    monkeypatch.chdir(_repo(tmp_path))
    assert commits_after("no-such-tag-anywhere") == []


def test_this_repository_is_tagged_for_submission() -> None:
    """Run against the real repository, and **unconditionally**. The old version returned
    early when a tag existed, which silenced it precisely when it began to matter."""
    assert tag_exists(), "the submission tag is missing; rule 41 requires one [AE-41]"
    assert is_annotated(), "the submission tag is lightweight; rule 41 wants provenance"
