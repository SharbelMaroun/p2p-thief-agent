"""`M9-019`: the submission tag names the reviewed commit, not a later one.

Rule 41 wants an annotated `v1.0-submission` tag on the accepted submission commit, "not at a
later commit written after the deadline". The failure is ordinary: you tag, then fix one more
thing, then push. The tag still exists and the repository still looks tidy — it simply names a
commit nobody reviewed.

There is no tag yet, so the interesting tests are the ones that work without one: the checker
must report *what to do* rather than crash, and each predicate must be exercised against real
Git rather than a mock, because every one of them is a question about this repository.
"""

from __future__ import annotations

from scripts.check_submission_tag import (
    TAG,
    commits_after,
    is_annotated,
    main,
    tag_exists,
)


def test_the_tag_name_is_the_one_rule_41_asks_for() -> None:
    assert TAG == "v1.0-submission"


def test_it_reports_a_missing_tag_rather_than_failing() -> None:
    """**The state this repository is in until submission.** "Have I tagged correctly?" has
    a useful answer before a tag exists, and it is not a traceback."""
    assert main() in (0, 1)


def test_a_missing_tag_prints_the_command_to_create_it(capsys) -> None:
    if tag_exists():
        return
    main()
    output = capsys.readouterr().out
    assert "git tag -a" in output and TAG in output


def test_the_predicates_run_against_real_git(capsys) -> None:
    """Each is a question about this repository, so none is mocked. A checker whose parts
    were all doubled would pass in a repository it had never actually looked at."""
    assert isinstance(tag_exists(), bool)
    assert isinstance(is_annotated(), bool)
    assert isinstance(commits_after(), list)


def test_a_nonexistent_tag_reports_no_later_commits_rather_than_erroring() -> None:
    """`rev-list absent..HEAD` fails; returning an empty list keeps the *reason* for failure
    with the tag-exists check, where the message can explain it."""
    assert commits_after("no-such-tag-anywhere") == []
