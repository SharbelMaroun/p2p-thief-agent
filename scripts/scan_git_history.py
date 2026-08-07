"""Scan every blob in Git history for secrets, not just the working tree (`M9-018`).

`check_secrets.py` scans the files that exist now. That is the wrong question for
submission: rule 39 forbids secrets being *in the repository*, and a credential deleted in
a later commit is still in the repository — every clone carries it, and `git log -p` prints
it. A working-tree scan reports clean on a repository that leaks.

**This is the check that gets more expensive the longer it is left.** Removing a blob means
rewriting history, which invalidates every existing clone and every commit hash after the
bad one — including any hash already recorded in an emitted artifact under rule 53. Run it
early and often; the cost of a finding grows with every commit added.

Two things are scanned, because a file can be a credential without containing a pattern
that looks like one:

* **blob contents**, through `check_secrets.line_findings` — deliberately the same
  function, so history and the working tree can never disagree about what counts;
* **paths**, against the names `.gitignore` exists to exclude. A committed `token.json` is a
  finding whatever is inside it.

A finding is not fixed by deleting the file. **Rotate the credential first** — a key that
reached a commit is compromised the moment it was pushed, and history rewriting is damage
control, not a remedy.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.check_secrets import TEXT_FILENAMES, TEXT_SUFFIXES, line_findings  # noqa: E402

# Paths that must never appear in history at all, whatever their contents. These mirror the
# `.gitignore` entries rules 39/40 require; a name is evidence on its own.
FORBIDDEN_NAMES = ("credentials.json", "token.json", ".env")
FORBIDDEN_SUFFIXES = (".key", ".pem", ".p12")
MAX_BLOB_BYTES = 2_000_000  # a blob larger than this is not hand-written configuration


class ShallowHistoryError(RuntimeError):
    """Raised when the clone has no history to scan."""


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True,
                            errors="replace", check=True)
    return result.stdout


def is_shallow() -> bool:
    """Whether this clone was truncated (`git clone --depth`, `actions/checkout` default).

    **This check is the difference between a security gate and a decoration.** A shallow
    clone contains only the tip commit, so `rev-list --all` returns the current tree and
    nothing else — the scan finds no secrets because there is no history to find them in,
    and prints exactly the same "0 findings" as a genuinely clean repository.

    Discovered on 2026-08-07 from a CI failure: `actions/checkout` defaults to
    `fetch-depth: 1`, and this scanner reported 441 objects where a full clone has 1709.
    It was reporting OK on 26% of the repository.
    """
    return _git("rev-parse", "--is-shallow-repository").strip() == "true"


def every_blob() -> list[tuple[str, str]]:
    """Every (sha, path) reachable from any ref, including deleted and rewritten files.

    `--all` matters more than it looks: scanning only `HEAD` misses a secret committed on a
    branch that was merged and deleted, which is exactly where one hides.
    """
    listing = _git("rev-list", "--objects", "--all")
    blobs: list[tuple[str, str]] = []
    for line in listing.splitlines():
        sha, _, path = line.partition(" ")
        if path:
            blobs.append((sha, path))
    return blobs


def forbidden_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return (name in FORBIDDEN_NAMES
            or name.startswith(".env") and not name.endswith("-example")
            or name.endswith(FORBIDDEN_SUFFIXES))


def scannable(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name in TEXT_FILENAMES or Path(name).suffix.lower() in TEXT_SUFFIXES


def first_commit_touching(path: str) -> str:
    """The earliest commit that introduced this path, so a rewrite has a starting point."""
    try:
        log = _git("log", "--all", "--reverse", "--format=%H", "--", path)
    except subprocess.CalledProcessError:
        return "unknown"
    return log.split("\n", 1)[0].strip() or "unknown"


def scan() -> list[str]:
    """Return every finding across all of history."""
    findings: list[str] = []
    seen_paths: set[str] = set()
    for sha, path in every_blob():
        if forbidden_path(path) and path not in seen_paths:
            seen_paths.add(path)
            findings.append(
                f"{path}: committed credential file (introduced {first_commit_touching(path)})")
        if not scannable(path):
            continue
        try:
            content = _git("cat-file", "blob", sha)
        except subprocess.CalledProcessError:
            continue
        if len(content) > MAX_BLOB_BYTES:
            continue
        for number, line in enumerate(content.splitlines(), start=1):
            for label in line_findings(line):
                findings.append(f"{path}@{sha[:12]}:{number}: {label}")
    return findings


def main() -> int:
    """Scan history and fail when anything that looks like a secret is present."""
    try:
        if is_shallow():
            print("REFUSING TO SCAN: this is a shallow clone, so there is no history to "
                  "read. A scan here would report '0 findings' after looking at the tip "
                  "commit alone — indistinguishable from a clean repository.\n"
                  "  CI: set `fetch-depth: 0` on actions/checkout.\n"
                  "  Locally: `git fetch --unshallow`.")
            return 2
        blobs = every_blob()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"could not read Git history: {exc}")
        return 2
    findings = scan()
    if findings:
        print(f"Possible secrets in Git history ({len(findings)} finding(s)):")
        print(*findings[:200], sep="\n")
        if len(findings) > 200:
            print(f"... and {len(findings) - 200} more")
        print("\nRotate the credential FIRST. A key that reached a commit is compromised "
              "from the moment it was pushed; rewriting history is damage control, not a fix.")
        return 1
    print(f"Git history scan OK: {len(blobs)} objects checked; 0 findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
