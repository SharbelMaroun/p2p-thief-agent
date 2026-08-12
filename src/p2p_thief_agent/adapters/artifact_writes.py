"""Write the pre-game declaration and per-sub-game config artifacts (companion `C-043`).

The builders (`reporting/declaration.py`, `reporting/config_artifact.py`) existed with
tests and no serve-path caller -- the same unwired pattern as the wire recorder and
`build_result` before them -- so every Thief-role sub-game left the four-family
artifact set (`inst/:2227`) missing its declaration and config members. Wired from
`post_match.finalise`, which is the moment negotiation facts and the peer identity
are all in hand.

The opponent's group block is built with `null` + `undeclared` for anything the peer
did not send: inventing a spec for them is rule 38's absolute disqualification, and
the builder's own `_check_disclosure` enforces exactly that honesty.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from p2p_thief_agent.orchestration.series import NUM_SUB_GAMES
from p2p_thief_agent.reporting.config_artifact import _SECTIONS, build_config
from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.emit import write_artifact
from p2p_thief_agent.reporting.naming import (
    MatchIdentity,
    config_filename,
    declaration_filename,
    match_filenames,
)
from p2p_thief_agent.shared.git_info import GitInfoError, running_git_commit

try:  # resolved once; a non-git deployment still writes an honest log
    RUNNING_COMMIT = running_git_commit()
except GitInfoError:
    RUNNING_COMMIT = "unknown"


def log_context(
    *,
    sha: str,
    sub_game: int,
    identity: Mapping[str, object],
    opponent_group_id: object,
    started_at: object,
    confirmed: bool,
    opponent_commit: object = "unknown",
) -> dict:
    """Build the log artifact's context block.

    Lifted out of `serve.py` unchanged apart from `confirmed`, which used to be the literal
    `True`.
    """
    return {
        "game_id": f"game-{sha[:12]}",
        "game_uid": sha[:32],
        "sub_game": sub_game,
        "group_id": identity.get("group_id", "unknown"),
        "opponent_group_id": opponent_group_id,
        "config_sha256": sha,
        "confirmed": confirmed,
        "started_at": started_at,
        "github_commit": {str(identity.get("group_id", "unknown")): RUNNING_COMMIT,
                          str(opponent_group_id): str(opponent_commit)},
    }



_SPEC_ALIASES = {"cpu": "cpu_type", "gpu": "gpu_model"}
_SPEC_KEYS = ("os", "cpu_type", "cpu_freq_mhz", "cpu_cores", "ram_gb",
              "gpu_model", "vram_gb")


def _conforming_spec(spec: object) -> dict | None:
    """Return a spec under our declaration's key set, or None if it cannot conform.

    A peer's spec arrives under its own vocabulary; known aliases are mapped, and
    anything still missing makes the whole spec unusable -- recorded as withheld
    rather than partially invented, because rule 38 forbids filling in a spec and
    the builder rightly refuses a partial one.
    """
    if not isinstance(spec, Mapping) or not spec:
        return None
    named = {_SPEC_ALIASES.get(k, k): v for k, v in spec.items()}
    if any(key not in named for key in _SPEC_KEYS):
        return None
    return {key: named[key] for key in _SPEC_KEYS}


def _group_block(identity: Mapping[str, object], *, ours: bool) -> dict:
    """Map a negotiation identity onto the declaration's group entry, honestly."""
    spec = identity.get("spec")
    model = identity.get("llm_model")
    block = {
        "group_id": identity.get("group_id"),
        "group_name": identity.get("group_name") or identity.get("group_id"),
        "members": identity.get("members") or [],
        "repos": identity.get("repos") or {},
        "mcp_servers": identity.get("mcp_servers") or {},
        "llm_model": model if isinstance(model, str) and model else None,
        "hardware_spec": _conforming_spec(spec),
    }
    if not ours:
        withheld = [name for name in ("llm_model", "hardware_spec") if block[name] is None]
        if withheld:
            block["undeclared"] = withheld
    # The declaration requires a `signature` member per group: ours commits to the
    # block itself (the companion Cop signs identically); a peer's is None, since
    # only a group can sign its own declaration and inventing one would be forgery.
    from p2p_thief_agent.protocol.crypto import canonical_sha256  # noqa: PLC0415

    block["signature"] = canonical_sha256(block) if ours else None
    return block


def write_pre_game_artifacts(
    directory: Path,
    *,
    context: Mapping[str, object],
    identity: Mapping[str, object],
    peer_identity: Mapping[str, object],
    game_config: Mapping[str, object],
    started_at: str,
    github_commit: str,
) -> None:
    """Write `config_<id>_gNN.json` always, and `declaration_<id>.json` once."""
    match = MatchIdentity(game_id=str(context["game_id"]), game_uid=str(context["game_uid"]))
    sub_game = int(context.get("sub_game", 1))  # type: ignore[call-overload]
    agreed = [str(identity.get("group_id")), str(peer_identity.get("group_id", "unknown"))]
    write_artifact(
        directory, config_filename(match.game_id, sub_game),
        build_config(
            identity=match, sub_game_number=sub_game, agreed_between=agreed,
            sections={name: game_config[name] for name in _SECTIONS},  # type: ignore[index]
            links=match_filenames(match, [sub_game]), config_name="game.json",
        ),
    )
    declaration_path = Path(directory) / declaration_filename(match.game_id)
    if declaration_path.exists():
        return  # the declaration is series-static: written by the first sub-game only
    league = game_config.get("network_and_league") or {}
    num_games = int(league.get("num_games", NUM_SUB_GAMES))  # type: ignore[union-attr]
    budget = int(league.get("token_budget_per_series", 0))  # type: ignore[union-attr]
    write_artifact(
        directory, declaration_filename(match.game_id),
        build_declaration(
            identity=match,
            groups=[_group_block(identity, ours=True), _group_block(peer_identity, ours=False)],
            num_sub_games=num_games,
            max_tokens_per_game=budget // num_games if num_games else 0,
            timezone="UTC", started_at=started_at, ended_at=started_at,
            links=match_filenames(match, list(range(1, num_games + 1))),
            github_commit=github_commit,
        ),
    )
