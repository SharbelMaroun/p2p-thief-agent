"""Naming one played sub-game's log: the identity every artifact of the series shares.

Split from `post_match.py` under the file-length gate, at a seam worth having on its own:
deciding *what a sub-game is called* is a different job from deciding *what happens after
the last move*, and getting the first wrong is how friendly-9 shipped three identities for
one series -- this side's log carrying the unlabelled uid, the companion Cop's carrying
`config_sha256[:32]`, and the result carrying the agreed value.

Everything here is computed rather than defaulted. A default is precisely how this
repository and the companion drifted into two naming schemes for one G009 series.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping


def series_log_context(
    *,
    agreement: object,
    game_config: Mapping[str, object],
    identity: Mapping[str, object],
    sub_game: int,
    started_at: object,
    audited: bool,
    series_game_id: str,
    log_context: Callable[..., dict],
) -> dict:
    """Build the log context for one finished sub-game, fully identified.

    `log_context` is injected so this module stays free of the artifact-writing layer it
    names for -- the same reason the caller passes it rather than importing it here.
    """
    from p2p_thief_agent.protocol.crypto import canonical_sha256
    from p2p_thief_agent.protocol.terms_projection import terms_from_shared_config
    from p2p_thief_agent.shared.series_identity import derive_game_uid, series_label

    peer = getattr(agreement, "peer_identity", {}) or {}
    opponent_gid = str(peer.get("group_id", "unknown"))
    groups = [str(identity.get("group_id", "unknown")), opponent_gid]
    return log_context(
        sha=canonical_sha256(dict(game_config)),
        sub_game=sub_game,
        identity=identity,
        opponent_group_id=peer.get("group_id", "unknown"),
        started_at=started_at,
        confirmed=audited,
        opponent_commit=peer.get("git_commit_hash", "unknown"),
        game_id=series_game_id,
        # The LABEL is threaded, not dropped. Without it this log carried the unlabelled
        # uid while the result carried the labelled one -- two names for one series inside
        # our own evidence.
        game_uid=derive_game_uid(
            terms_from_shared_config(dict(game_config)), groups,
            series_label(series_game_id, groups)),
    )
