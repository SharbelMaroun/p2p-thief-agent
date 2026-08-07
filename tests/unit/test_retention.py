"""`M7-008a`: every game's config is written where the repository can carry it.

Appendix F's fourth obligation requires each game's configuration to be committed. The
finding that produced this module is that **we were not doing it**: `.gitignore` excludes
`logs/`, `reports/generated/` and `results/generated/`, so an artifact written under any of
them exists on one laptop and nowhere the obligation can see.

That failure is silent — the write succeeds and the file is present — so these tests are
weighted towards it. The one that matters most reads the real `.gitignore` and fails if
`games/` is ever added to it, because the realistic way this regresses is somebody tidying
the working tree. Retrieval (`M7-008b`) is in `test_retention_retrieval.py`.
"""

from __future__ import annotations

import pathlib

import pytest

from p2p_thief_agent.reporting.naming import MatchIdentity
from p2p_thief_agent.reporting.retention import (
    COMMITTED_GAMES_DIR,
    IGNORED_PATHS,
    RetentionError,
    game_directory,
    store_config,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
IDENTITY = MatchIdentity(game_id="demo-vs-rival", game_uid="u" * 32)
CONFIG = {"_schema": "config", "scoring": {"capture": -10}, "config_sha256": "a" * 64}


def gitignore_lines() -> set[str]:
    text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    return {line.strip().rstrip("/") for line in text.splitlines()
            if line.strip() and not line.startswith("#")}


# --- the guard against the failure that produced this module --------------------------------


def test_the_committed_games_directory_is_not_excluded_by_gitignore() -> None:
    """**The test this module exists for.** `games/` must stay committable, and the way
    this regresses is somebody adding it to `.gitignore` to keep the tree tidy — the same
    reasoning that put `logs/` there and lost every config with it."""
    assert COMMITTED_GAMES_DIR not in gitignore_lines(), (
        f"{COMMITTED_GAMES_DIR}/ is excluded; Appendix F obligation 4 requires every "
        "game's config to be committed")


def test_every_refused_path_is_one_gitignore_actually_excludes() -> None:
    """The refusal list is data, not a reading of `.gitignore` — a guard that derives its
    rule from the file it checks agrees with itself by construction. This asserts the two
    still say the same thing, matched against **whole lines**: an earlier version checked
    `"results/" in text`, which passed on the substring of `results/generated/` while the
    guard refused a `results/` that is perfectly committable."""
    lines = gitignore_lines()
    for ignored in IGNORED_PATHS:
        joined = "/".join(ignored)
        assert joined in lines, f"{joined}/ is refused but no longer ignored — drop it"


def test_storing_under_an_ignored_root_is_refused(tmp_path) -> None:
    """The write would succeed and the file would be there; only the commit would be
    missing, which is the part nobody notices until grading."""
    with pytest.raises(RetentionError, match="obligation 4"):
        store_config(tmp_path / "logs", IDENTITY, 1, CONFIG)


@pytest.mark.parametrize("ignored", IGNORED_PATHS)
def test_every_ignored_path_is_refused_at_any_depth(tmp_path, ignored) -> None:
    """Matched as a run of components, so a nested `build/logs/games` is caught too — the
    shape a path assembled from a base directory and a suffix actually takes."""
    with pytest.raises(RetentionError):
        store_config(tmp_path.joinpath(*ignored) / "nested", IDENTITY, 1, CONFIG)


def test_a_committable_directory_sharing_a_name_with_an_ignored_one_is_allowed(
    tmp_path,
) -> None:
    """`results/generated/` is ignored; `results/` is not. Refusing the parent would send a
    caller hunting for a problem that is not there."""
    assert store_config(tmp_path / "reports", IDENTITY, 1, CONFIG).is_file()


# --- M7-008a: stored under a game_id-derived name -------------------------------------------


def test_a_config_is_stored_under_a_game_id_derived_path(tmp_path) -> None:
    path = store_config(tmp_path, IDENTITY, 1, CONFIG)
    assert path.parent == game_directory(tmp_path, IDENTITY.game_id)
    assert path.name == "config_demo-vs-rival_g01.json"


def test_each_sub_game_gets_its_own_file(tmp_path) -> None:
    """Six sub-games, six configs. A single file per match would let a later sub-game's
    negotiated terms overwrite an earlier one's, and the overwritten game becomes
    irreproducible with nothing to show it happened."""
    for number in (1, 2, 3):
        store_config(tmp_path, IDENTITY, number, {**CONFIG, "sub_game_number": number})
    stored = list(game_directory(tmp_path, IDENTITY.game_id).iterdir())
    assert len(stored) == 3


def test_a_game_id_that_could_climb_out_of_the_directory_is_refused(tmp_path) -> None:
    """`game_id` is negotiated with an opponent, so it is untrusted input reaching the
    filesystem."""
    for hostile in ("../escape", "a/b", ".."):
        with pytest.raises(RetentionError, match="cannot address a directory"):
            game_directory(tmp_path, hostile)
