"""`M9-018`: every blob in history is scanned, not just the files that exist now.

Rule 39 forbids secrets being *in the repository*. A credential deleted three commits ago is
still in the repository — every clone carries the blob and `git log -p` prints it — so a
working-tree scan can report clean on a repository that leaks. This module holds the
scanner honest.

**This repository's history is currently clean**, which is exactly when a scanner's tests
matter: nothing is failing, so nothing would notice if the scan silently stopped looking.
Hence the emphasis below on the ways a structural check goes quietly vacuous — a `--all`
that became `HEAD`, a suffix filter that opened nothing, a scan that inspected 3 objects and
reported success.

The companion repository needed a reviewed-findings mechanism because its history contains a
false positive that can no longer be edited. This one does not have that table, and should
not gain one until it has something real to review — an unused suppression mechanism is a
suppression mechanism somebody eventually uses.
"""

from __future__ import annotations

import pytest

from scripts.check_secrets import line_findings
from scripts.scan_git_history import (
    FORBIDDEN_NAMES,
    FORBIDDEN_SUFFIXES,
    every_blob,
    forbidden_path,
    is_shallow,
    scannable,
)

# --- the ways a history scan goes quietly vacuous ------------------------------------------


def test_a_shallow_clone_is_refused_rather_than_scanned() -> None:
    """**The defect CI found on 2026-08-07, and the reason this file exists.**

    `actions/checkout` defaults to `fetch-depth: 1`. On that clone `rev-list --all` returns
    the tip tree and nothing else, so the scan reported 441 objects where a full clone has
    over 1700 — and would have printed "0 findings" for a repository it had barely read.
    Identical output to a genuinely clean history.

    I did not reason my way to this. Two environment-dependent assertions in this very file
    failed in CI, which is the only reason it surfaced; the scan itself passed silently.
    """
    assert callable(is_shallow)
    assert is_shallow() is False, (
        "this checkout is shallow — the scan cannot see history. CI must set "
        "`fetch-depth: 0`; locally, `git fetch --unshallow`")


def test_the_scan_reaches_the_whole_history_rather_than_one_commit() -> None:
    """`--all` dropped to `HEAD` still reports "OK"; it just stops seeing the deleted branch
    where a secret hides. The threshold is deliberately far below the real count — it is
    guarding against *one commit*, not tracking repository size."""
    blobs = every_blob()
    assert len(blobs) > 500, f"only {len(blobs)} objects — is `--all` still passed?"


def test_history_contains_paths_that_no_longer_exist_on_disk() -> None:
    """Proof the scan sees more than the working tree. If every historical path still
    existed, this scanner would be an expensive duplicate of `check_secrets.py` — which is
    exactly what a shallow clone silently turns it into."""
    import pathlib  # noqa: PLC0415

    root = pathlib.Path(__file__).resolve().parents[2]
    gone = [path for _, path in every_blob() if not (root / path).exists()]
    assert gone, "no deleted path found in history — the scan may be reading the tree"


def test_the_text_filter_admits_the_files_secrets_actually_live_in() -> None:
    """A suffix set that quietly excluded `.py` and `.json` would scan nothing that
    matters and still print a large object count."""
    for path in ("a.py", "config.json", "notes.md", "pyproject.toml", "x.yaml"):
        assert scannable(path), f"{path} is not being opened"


@pytest.mark.parametrize("path", ["logo.png", "font.woff2", "archive.zip"])
def test_binary_blobs_are_skipped(path: str) -> None:
    assert not scannable(path)


# --- a name is evidence on its own ----------------------------------------------------------


@pytest.mark.parametrize("path", ["credentials.json", "a/b/token.json", "server.pem",
                                  "id.key", "x.p12", ".env", "deep/.env.production"])
def test_a_credential_path_is_a_finding_whatever_it_contains(path: str) -> None:
    """A file can be a credential without containing anything a pattern matches — an
    empty-looking `token.json` is still a committed credential file."""
    assert forbidden_path(path)


@pytest.mark.parametrize("path", [".env-example", "src/keyring_helper.py", "README.md",
                                  "docs/PRD_gatekeeper_reporting.md"])
def test_an_innocent_path_is_not_flagged(path: str) -> None:
    """`.env-example` is committed deliberately: it documents which variables exist without
    holding any of their values."""
    assert not forbidden_path(path)


def test_every_forbidden_name_is_one_gitignore_also_excludes() -> None:
    """The two lists answer the same question — what must never be committed — and a name
    refused here but not ignored there means the next `git add .` re-adds it `[AE-40]`."""
    import pathlib  # noqa: PLC0415

    ignored = (pathlib.Path(__file__).resolve().parents[2] / ".gitignore").read_text(
        encoding="utf-8")
    for name in FORBIDDEN_NAMES:
        assert name in ignored, f"{name} is refused in history but not gitignored"
    for suffix in FORBIDDEN_SUFFIXES:
        assert f"*{suffix}" in ignored, f"*{suffix} is refused in history but not gitignored"


# --- the detector is shared, not restated ---------------------------------------------------


def test_the_history_scan_uses_the_same_rules_as_the_working_tree_gate() -> None:
    """`line_findings` is imported rather than reimplemented. Two copies of a security rule
    drift in exactly one direction, and the copy nobody looks at is the one that goes
    stale."""
    # Joined at runtime: this file is scanned too, and a literal here would fail the gate
    # it is asserting about.
    assert line_findings("api_key = " + '"live-value-here"')
    assert line_findings("    access_token" + ": str") == [], "the shared detector changed"


def test_this_repository_has_no_reviewed_findings_table() -> None:
    """**Deliberate.** The companion repository has one because its history holds a false
    positive that can no longer be edited. An unused suppression mechanism is a suppression
    mechanism somebody eventually reaches for, so this one stays absent until there is
    something real to review."""
    import scripts.scan_git_history as scanner  # noqa: PLC0415

    assert not hasattr(scanner, "REVIEWED_HISTORY")
