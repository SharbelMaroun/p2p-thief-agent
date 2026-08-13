"""The one identifier that names every artifact in a series (`AF-021`, Appendix F t20).

Mirrors the companion Cop's module of the same name. It is duplicated rather than shared
because the two repositories must stay independently clonable (`THIEF-002`, rule 49) --
but the *derivations* below are pinned to produce byte-identical results to that side,
and a test asserts the shared UUID rather than trusting the coincidence.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Mapping, Sequence


def series_game_id(config: Mapping[str, object]) -> str:
    """Return the agreed ``G00N`` label from the private config.

    Appendix F table 20 (p. 141/289) names all four artifacts from ``<game_id>``::

        declaration_<game_id>.json
        config_<game_id>_g<NN>.json
        log_<game_id>_g<NN>.json
        result_<game_id>.json

    and the book states the identifier is the label the two teams agree or the league
    assigns -- **not** a value derived from a hash of the configuration, whose only job is
    locking the config under ``config_sha256``. The reference derives a *human* id from the
    agreed terms plus both group ids (`domain/game_ids.py: derive_game_ids`), so both peers
    reach it without an extra round trip. Neither source supports a config digest.

    **This side's version of the defect, found live in a counted game.** The companion was
    fixed on 2026-08-13 and this one was not, so `G009` sub-game 1 -- a Thief turn, written
    here -- produced ``log_game-5a7b4a6e58be_g01.json`` while the companion's sub-game 2
    produced ``config_G009_g02.json``. One series, two naming schemes, and a result report
    that would link six files of which only three existed. The series was stopped at that
    point. The lesson is the one the companion's fix already recorded and this repository
    did not act on: the two halves of an artifact set are written by two repositories that
    cannot see each other, so a fix in one is not a fix.

    Refuses rather than defaulting: a missing label fails at launch, where it costs one
    restart, instead of at grading, where it cannot be fixed.
    """
    game = config.get("game")
    label = ""
    if isinstance(game, Mapping):
        label = str(game.get("series_game_id") or "").strip()
    if not label:
        raise ValueError(
            "[game].series_game_id is required -- it names every artifact in the set "
            "(declaration_<id>.json, config_<id>_gNN.json, log_<id>_gNN.json, "
            "result_<id>.json). Agree the G00N label with the opponent and set it in the "
            "private game.toml. It is never derived from the config hash."
        )
    return label


def derive_game_uid(terms: Mapping[str, object], group_ids: Sequence[str]) -> str:
    """The shared derivation: a UUID from the agreed terms and the sorted group pair.

    Byte-compatible with the companion's `reporting/series_consensus.derive_game_uid` and
    with `uoh-ay26`'s implementation -- all three independently produced
    ``7b1d942e-5a9c-6e0c-312a-761dd7dec131`` for the G005/G009 terms, which is what makes
    it usable as the shared identifier the four artifacts are supposed to share.

    Replaces ``config_sha256[:32]``, a value only this side computed, so the log carried an
    identifier that appeared in no report from either team.
    """
    seed = (json.dumps(dict(terms), sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")).encode("utf-8")
            + b"|" + "|".join(sorted(group_ids)).encode("utf-8"))
    return str(uuid.UUID(bytes=hashlib.sha256(seed).digest()[:16]))


def series_game_id_from_private(private: object) -> str:
    """Read the agreed label straight from a private-config path.

    Lives here rather than as a private helper in `adapters/play_command.py`: that file was
    two lines under the 150-line gate, and the reader belongs beside the value it reads
    anyway. Refuses a missing `--private` for the same reason `series_game_id` refuses a
    missing label -- there is no honest artifact name without it.
    """
    from pathlib import Path  # noqa: PLC0415

    from p2p_thief_agent.shared.private_config import load_private_config  # noqa: PLC0415

    if private is None:
        raise ValueError(
            "--private is required: [game].series_game_id names every artifact written "
            "(declaration_<id>.json, config_<id>_gNN.json, log_<id>_gNN.json)"
        )
    return series_game_id(load_private_config(Path(private)))
