"""Is every artifact that must be committed actually tracked by Git (`M9-023`)?

**The obligations differ per artifact, and treating them alike gets one of them wrong.** Both
notebooks were asked on 2026-08-07 and the book's answer is not "commit all four":

* **Config — mandatory.** Appendix F obligation 4 (p.140/288): "It is mandatory to attach
  each game's configuration file to the GitHub repository." This is the only hard commit
  obligation, and it is the row that fails this script.
* **Game log — not in §9.4.1's minimum contents**, but required to run the Replay app, which
  is itself a threshold condition for submission (p.129/272, rule 20). So a log for a game we
  intend to *demonstrate* has to be reachable; one for every warm-up does not.
* **Final result — no commit obligation at all.** Its duty is to be emailed (rule 51,
  p.133/279).
* **Declaration — no commit obligation** beyond travelling with its game.

An earlier note in `games/README.md` justified excluding logs on the grounds that committing
them would publish nonces. **That reasoning was wrong** and is corrected there: rule 18
(`inst/:3354`) keeps a nonce secret *until the end of the game*, and Step 4 is the Final
Reveal where "all values, including the Nonce, are revealed for a full mutual audit"
(`inst/:1136`). A finished log's nonces are meant to be public. The reason logs are not
committed wholesale is simply that no rule asks for it.

"Committed" is asked of **Git**, not of the filesystem. A file present on disk and untracked
is exactly the state Appendix F obligation 4 exists to prevent, and it is invisible to any
check that only calls `Path.exists()`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMITTED_GAMES_DIR = "games"


def tracked_paths() -> set[str]:
    """Every path Git currently tracks, as forward-slash relative strings."""
    listing = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                             check=True, cwd=ROOT).stdout
    return {line.strip() for line in listing.splitlines() if line.strip()}


def committed_configs(tracked: set[str]) -> dict[str, list[str]]:
    """Configs under `games/`, grouped by `game_id`."""
    grouped: dict[str, list[str]] = {}
    prefix = f"{COMMITTED_GAMES_DIR}/"
    for path in sorted(tracked):
        if not path.startswith(prefix) or not path.endswith(".json"):
            continue
        parts = path.split("/")
        if len(parts) >= 3:
            grouped.setdefault(parts[1], []).append(parts[-1])
    return grouped


def untracked_configs() -> list[str]:
    """Config files sitting under `games/` that Git does not track.

    **The failure this script exists for.** The file is on disk, a directory listing shows
    it, and it is missing from the only place the obligation looks.
    """
    games_root = ROOT / COMMITTED_GAMES_DIR
    if not games_root.is_dir():
        return []
    tracked = tracked_paths()
    on_disk = {p.relative_to(ROOT).as_posix() for p in games_root.rglob("*.json")}
    return sorted(on_disk - tracked)


def main() -> int:
    """Report what the obligation covers, and what is missing from Git."""
    try:
        tracked = tracked_paths()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"could not ask Git what is tracked: {exc}")
        return 2

    stray = untracked_configs()
    if stray:
        print("Config files on disk but NOT tracked by Git "
              "(Appendix F obligation 4 requires each game's config committed):")
        print(*(f"  - {path}" for path in stray), sep="\n")
        print("\n`git add games/` — a file present on disk and untracked is exactly the "
              "state the obligation exists to prevent.")
        return 1

    grouped = committed_configs(tracked)
    if not grouped:
        print("No committed game configs yet. Expected until the first counted game is "
              "played; `reporting/retention.store_config` writes them under games/<game_id>/.")
        return 0
    print(f"Committed configs OK: {len(grouped)} game(s) tracked by Git.")
    for game_id, files in sorted(grouped.items()):
        print(f"  - {game_id}: {len(files)} config(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
