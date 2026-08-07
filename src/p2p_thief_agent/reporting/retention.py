"""Every game's config, kept where the repository can carry it (`M7-008`).

Appendix F's fourth obligation requires each game's configuration to be committed to the
repository, so any past game can be reproduced from what is checked in rather than from
whatever is left on the machine that played it.

**The reference implementation does not do this**, and neither did we: `.gitignore` excludes
`logs/`, `reports/generated/` and `results/generated/`, so an artifact written under any of
them is retained on one laptop and lost to the repository. That is a defensible default for
run output — it keeps a working tree from filling with noise — and exactly wrong for the one
artifact an obligation says to commit.

So configs go to `games/`, which is deliberately *not* ignored, and `store_config` refuses a
destination under an ignored root rather than writing a file that will never be committed.
The failure it prevents is silent: the write succeeds, the file is there, and it is missing
only from the thing that matters.

Committing configs is safe **because** the privacy guards already exist. `config_privacy`
and `protocol/outbound_fields` keep strategy, LLM and credential fields out of the shared
config, so what lands in `games/` is the negotiated match terms and nothing else — rule 39
forbids pushing secrets to the repository "even if it is private and shared only with the
lecturer", and this is what makes obligation 4 and rule 39 satisfiable at once.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from p2p_thief_agent.reporting.emit import write_artifact
from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity, config_filename

COMMITTED_GAMES_DIR = "games"

# Paths `.gitignore` excludes, as component runs rather than single names. `logs/` is ignored
# wholesale, but only `reports/generated/` and `results/generated/` are — a bare `reports/`
# is committable, and refusing it would send a caller hunting for a problem that is not
# there. Kept as data rather than parsed from `.gitignore` so a test can assert the two
# agree; a guard that derives its rule from the file it checks agrees with itself.
IGNORED_PATHS: tuple[tuple[str, ...], ...] = (
    ("logs",), ("reports", "generated"), ("results", "generated"),
)


class RetentionError(ArtifactError):
    """Raised when a config would be stored somewhere the repository cannot carry it."""


def game_directory(root: Path, game_id: str) -> Path:
    """Where one match's committed configs live.

    Per `game_id` rather than one flat directory: a series is six configs, and a flat
    directory makes "which configs belong to this match" a filename-parsing exercise for
    whoever audits it later.
    """
    if not game_id or "/" in game_id or "\\" in game_id or game_id in {".", ".."}:
        raise RetentionError(f"game_id {game_id!r} cannot address a directory")
    return Path(root) / COMMITTED_GAMES_DIR / game_id


def _refuse_ignored(root: Path) -> None:
    """Refuse a destination `.gitignore` excludes, matched as a run of path components.

    Component-wise rather than by string prefix: the realistic caller builds this path by
    joining a base directory onto something else, so the excluded run turns up in the
    middle (`build/logs/games`) rather than at the front.
    """
    parts = [part.lower() for part in Path(root).parts]
    for ignored in IGNORED_PATHS:
        width = len(ignored)
        runs = (tuple(parts[i:i + width]) for i in range(len(parts) - width + 1))
        if ignored in runs:
            raise RetentionError(
                f"{root} sits under {'/'.join(ignored)}/, which .gitignore excludes; a "
                "config written there is retained on this machine and lost to the "
                "repository, and Appendix F obligation 4 requires every game's config to "
                "be committed")


def store_config(
    root: Path, identity: MatchIdentity, sub_game_number: int, artifact: Mapping[str, object]
) -> Path:
    """Write one sub-game's config where the repository will carry it (`M7-008a`)."""
    _refuse_ignored(root)
    directory = game_directory(root, identity.game_id)
    return write_artifact(directory, config_filename(identity.game_id, sub_game_number),
                          artifact)


def retrieve_config(root: Path, game_id: str, sub_game_number: int) -> dict:
    """Read back any past game's config (`M7-008b`).

    The retrieval half is what makes retention checkable. A store with no reader is a claim
    that files exist somewhere; this is the operation an auditor actually performs, so it is
    the one the tests exercise.
    """
    path = game_directory(root, game_id) / config_filename(game_id, sub_game_number)
    if not path.is_file():
        raise RetentionError(
            f"no committed config for {game_id!r} sub-game {sub_game_number}; Appendix F "
            f"obligation 4 requires it and the game cannot be reproduced without it")
    return json.loads(path.read_text(encoding="utf-8"))


def stored_games(root: Path) -> tuple[str, ...]:
    """Every `game_id` with at least one committed config, sorted."""
    base = Path(root) / COMMITTED_GAMES_DIR
    if not base.is_dir():
        return ()
    return tuple(sorted(entry.name for entry in base.iterdir() if entry.is_dir()))


def missing_configs(root: Path, game_id: str, sub_game_numbers: tuple[int, ...]) -> tuple[int, ...]:
    """Which sub-games of a played series have no committed config.

    Returned rather than raised. This is the question asked *before* a submission, when the
    useful answer is the full list of gaps to fill — stopping at the first one turns a single
    review into six.
    """
    directory = game_directory(root, game_id)
    return tuple(number for number in sub_game_numbers
                 if not (directory / config_filename(game_id, number)).is_file())
