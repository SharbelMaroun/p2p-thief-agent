"""Artifact filenames and the shared match identity — the book-confirmed part of `M7-002`.

Two facts are book-confirmed and independent of the artifacts' internal schema. The four
artifacts of one match share a single `game_uid` (`AR-001`), and their filenames derive from
the `game_id` (`AF-021` / `AF-§3`): `declaration_<game_id>.json`,
`config_<game_id>_g<NN>.json`, `log_<game_id>_g<NN>.json`, `result_<game_id>.json`.

The exact **field schema** of each artifact is an open unknown (`U-019`): the observed template
in `docs/JSON_ARTIFACT_SCHEMAS.md` is unauthenticated, so this module fixes only the confirmed
naming and identity. The schema builders wait on the coordinator's `U-019` ruling rather than
implement a guessed schema.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from p2p_thief_agent.orchestration.series import NUM_SUB_GAMES


class ArtifactError(ValueError):
    """Raised when an artifact identity or filename is malformed."""


@dataclass(frozen=True, slots=True)
class MatchIdentity:
    """The identity every artifact of one match shares (`AR-001`)."""

    game_id: str
    game_uid: str

    def __post_init__(self) -> None:
        if not self.game_id or not self.game_uid:
            raise ArtifactError("game_id and game_uid must both be non-empty")


def _sub_game_tag(sub_game_number: int) -> str:
    if not 1 <= sub_game_number <= NUM_SUB_GAMES:
        raise ArtifactError(f"sub_game_number must be in 1..{NUM_SUB_GAMES}, got {sub_game_number}")
    return f"g{sub_game_number:02d}"


def declaration_filename(game_id: str) -> str:
    return f"declaration_{game_id}.json"


def result_filename(game_id: str) -> str:
    return f"result_{game_id}.json"


def config_filename(game_id: str, sub_game_number: int) -> str:
    return f"config_{game_id}_{_sub_game_tag(sub_game_number)}.json"


def log_filename(game_id: str, sub_game_number: int) -> str:
    return f"log_{game_id}_{_sub_game_tag(sub_game_number)}.json"


def match_filenames(identity: MatchIdentity, sub_game_numbers: Sequence[int]) -> dict[str, object]:
    """Every filename for a match, all derived from one `game_id` (`M7-002e`)."""
    if not sub_game_numbers:
        raise ArtifactError("a match must have at least one sub-game")
    return {
        "declaration": declaration_filename(identity.game_id),
        "result": result_filename(identity.game_id),
        "configs": [config_filename(identity.game_id, n) for n in sub_game_numbers],
        "logs": [log_filename(identity.game_id, n) for n in sub_game_numbers],
    }
