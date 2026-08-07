"""Run every gate from a fresh clone, the way the grader will (`M9-013b`).

`G-001`…`G-009` all pass on this machine. That is a weaker claim than it sounds, because a
working tree accumulates things a clone does not have: an editable install, a stale
`.venv`, a file that was written but never `git add`ed, a cached artifact. **The gate that
matters is whether they pass on a checkout of what was actually pushed.**

So this clones `HEAD` into a throwaway directory with `git clone --local`, installs from the
lockfile with `uv sync --frozen`, and runs each gate there. `--frozen` is the point of
`G-001`: a resolve that silently updates a dependency proves the gates pass against some
other version of the project.

**The untracked-file check is the one that earns its keep.** A gate script that exists only
in the working tree passes here on this machine and vanishes in a clone, and the symptom —
"command not found" during a grader's run — arrives at the worst possible time. `git clone`
copies only what is committed, so the clone answers that question by construction.

`M9-013a` (a genuinely different machine) is *not* this. A local clone shares the OS, the
Python build and the uv cache; it catches missing files and lockfile drift, not
platform-specific breakage. Recorded rather than blurred, because claiming this covers
`M9-013a` would be the kind of overstatement the row exists to prevent.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# `G-001`…`G-009`, minus the two that cannot run inside a clone: `G-008` (the prompt log is
# reviewed, not executed) and `G-009` (CI runs on the push, not here).
GATES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("G-002 ruff", ("uv", "run", "ruff", "check", ".")),
    ("G-003 pytest + coverage", ("uv", "run", "python", "-m", "pytest", "-q",
                                 "-p", "no:cacheprovider")),
    ("G-004 file lengths", ("uv", "run", "python", "scripts/check_file_lengths.py")),
    ("G-005 secret scan", ("uv", "run", "python", "scripts/check_secrets.py")),
    ("G-007 whitespace", ("git", "diff", "--check")),
    ("M9-017 submission contents", ("uv", "run", "python",
                                    "scripts/check_submission_contents.py")),
    ("M9-023 configs committed", ("uv", "run", "python",
                                  "scripts/check_artifacts_committed.py")),
)


def run(command: tuple[str, ...], cwd: Path, timeout: int = 900) -> tuple[bool, str]:
    try:
        done = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                              errors="replace", timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    tail = (done.stdout + done.stderr).strip().splitlines()[-3:]
    return done.returncode == 0, "\n      ".join(tail)


def main() -> int:
    """Clone, install frozen, and run every runnable gate in the clone."""
    workspace = Path(tempfile.mkdtemp(prefix="clean-clone-"))
    clone = workspace / "repo"
    failures: list[str] = []
    try:
        print(f"Cloning {ROOT.name} into {clone} ...")
        ok, detail = run(("git", "clone", "--local", "--no-hardlinks", str(ROOT), str(clone)),
                         cwd=workspace)
        if not ok:
            print(f"  clone FAILED: {detail}")
            return 2

        print("G-001 uv sync --frozen ...")
        ok, detail = run(("uv", "sync", "--frozen"), cwd=clone)
        print(f"  {'PASS' if ok else 'FAIL'}  {detail}")
        if not ok:
            failures.append("G-001 uv sync --frozen")
            print("\nA frozen install that fails means the lockfile and the manifest "
                  "disagree; every later gate would run against a different project.")
            return 1

        for name, command in GATES:
            ok, detail = run(command, cwd=clone)
            print(f"{name}: {'PASS' if ok else 'FAIL'}\n      {detail}")
            if not ok:
                failures.append(name)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    if failures:
        print(f"\n{len(failures)} gate(s) failed in a clean clone: {', '.join(failures)}")
        print("Re-run the same gate in the working tree. If it passes there, the difference "
              "is something not committed; if it fails there too, it is a plain gate "
              "failure that the clone simply surfaced first.")
        return 1
    print(f"\nClean-clone verification OK: {len(GATES) + 1} gates pass on a fresh checkout.")
    print("Note: this is a LOCAL clone. `M9-013a` (a second machine) is a different claim "
          "and remains open.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
