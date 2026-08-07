"""Pre-game declaration artifact (`M7-002a`).

**`U-019`-PROVISIONAL.** The field set follows the *observed* template recorded in
`docs/JSON_ARTIFACT_SCHEMAS.md` — unauthenticated, so requiredness/types/bounds are not
official. The coordinator authorised building against it pending a `U-019` ruling; the exact
schema may still change. Naming and the shared `game_uid` are book-confirmed (`M7-002e`).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from p2p_thief_agent.reporting.naming import ArtifactError, MatchIdentity

# Observed template value; Appendix B's example uses "1.2" (`C-008`/ADR-0003, unresolved).
SCHEMA_VERSION = "1.1"

_GROUP_KEYS = (
    "group_id", "group_name", "members", "repos", "mcp_servers", "llm_model",
    "hardware_spec", "signature",
)
# `inst/:1278` lists **Operating System first**: "Operating System (OS), number of processor
# cores and their frequency (CPU), RAM capacity, presence of a graphics card and video memory
# (GPU/VRAM)". `os` was missing here until 2026-08-07 — rule 24 is Mandatory and its sanction
# is denial of eligibility for computational bonuses, so an incomplete spec costs points.
# Adding it broke 19 fixtures, which is the evidence the field was genuinely never supplied.
_HARDWARE_KEYS = ("os", "cpu_type", "cpu_freq_mhz", "cpu_cores", "ram_gb", "gpu_model", "vram_gb")


def _require(data: Mapping, keys: Sequence[str], label: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ArtifactError(f"{label} missing fields: {sorted(missing)}")


def _check_disclosure(group: Mapping, *, ours: bool) -> None:
    """Rule 24 for us, `null` permitted for a peer that declared nothing (`M7-22f`).

    **Ours** must carry a complete spec: rule 24 is Mandatory and its sanction is denial of
    eligibility for the computational bonus, which `inst/:1276` describes as the mechanism
    for judging whether a phone raced a workstation fairly.

    **Theirs may be `null`**, and until 2026-08-07 it could not be — a `None` spec reached
    `_require` and died on `TypeError: argument of type 'NoneType' is not iterable`. That
    left a caller holding a peer that declared nothing with two options: drop the group, or
    invent a spec. The reference implementation takes the second, resolving it as
    `opp = series.peer_identity or own` — an empty peer identity is falsy, so it copies its
    **own** hardware and model into the opponent's slot, and its sample artifacts show two
    groups sharing one machine.

    That is a false statement in an artifact rule 38 makes an absolute disqualification to
    falsify. Refusing `null` here is what creates the pressure to make one, so `null` is
    accepted and `undeclared` names what was withheld — the omission stays theirs, legible,
    and rule 24's sanction lands where it belongs. The companion Cop reached the same
    resolution from the same finding.
    """
    spec, model = group.get("hardware_spec"), group.get("llm_model")
    if ours:
        if not isinstance(spec, Mapping) or not isinstance(model, str) or not model:
            raise ArtifactError(
                "our group must declare llm_model and hardware_spec; rule 24 is Mandatory "
                "and forfeits the computational bonus [AE-24]")
        _require(spec, _HARDWARE_KEYS, "hardware_spec")
        return
    if spec is not None:
        if not isinstance(spec, Mapping):
            raise ArtifactError("a peer hardware_spec must be an object or null")
        _require(spec, _HARDWARE_KEYS, "hardware_spec")
    withheld = [name for name, value in (("llm_model", model), ("hardware_spec", spec))
                if value is None]
    if withheld and sorted(group.get("undeclared") or []) != sorted(withheld):
        raise ArtifactError(
            f"group {group['group_id']!r} withheld {sorted(withheld)}, so the entry must "
            "carry `undeclared` naming exactly those. Recording the absence is what keeps "
            "us from filling it in [AE-38]")


def build_declaration(
    *,
    identity: MatchIdentity,
    groups: Sequence[Mapping],
    num_sub_games: int,
    max_tokens_per_game: int,
    timezone: str,
    started_at: str,
    ended_at: str,
    links: Mapping,
    github_commit: str,
) -> dict:
    """Assemble the pre-game declaration (`M7-002a`), sharing the match's `game_uid`.

    `github_commit` is **mandatory, not optional** (`M7-020`). Rule 53: "Record the commit
    hash in the declaration; it is permitted to change code between games, but for every
    game, you must update the commit hash." The field was missing entirely until
    2026-08-07 — the declaration named who was playing and on what hardware, but not
    *which code*, which is the one thing that makes a later audit reproducible.
    """
    if not groups:
        raise ArtifactError("a declaration must name at least one group")
    if not isinstance(github_commit, str) or len(github_commit) < 7:
        raise ArtifactError(
            "declaration needs the commit hash of the code that played this game [AE-53]")
    for index, group in enumerate(groups):
        _require(group, _GROUP_KEYS, "declaration group")
        _check_disclosure(group, ours=index == 0)
    return {
        "_schema": "declaration",
        "schema_version": SCHEMA_VERSION,
        "declaration_type": "pre_game",
        "game_id": identity.game_id,
        "game_uid": identity.game_uid,
        "links": dict(links),
        "timezone": timezone,
        "game_started_at": started_at,
        "game_ended_at": ended_at,
        "num_sub_games": num_sub_games,
        "max_tokens_per_game": max_tokens_per_game,
        "github_commit": github_commit,
        "groups": [dict(group) for group in groups],
    }
