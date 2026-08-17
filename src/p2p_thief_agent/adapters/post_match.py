"""Stay reachable after the last move, so the opponent's audit is not a 502 (`M7-018d`).

**The defect this exists to fix, seen live on 2026-08-11.** We played group `uoh-ay26`,
survived all 35 steps, wrote the log and **exited**. Their Cop then called `submit_audit`
on our endpoint, met a dead process behind a live tunnel, and recorded:

    Opponent unreachable mid-match -- resolving as technical loss:
    submit_audit timed out: ... Server error '502 Bad Gateway'

So our artifact said `survival` and theirs said `technical_loss`. Rule 35 scores conflicting
reports **0/0 for both**, which turned a clean win into nothing. Nothing was wrong with the
game; we simply left before the conversation was over.

**Rule 36 makes this mandatory, not polite.** The mutual audit is "a mandatory condition
before agreement", and an agreement needs two peers present. A peer that stops listening the
instant its own result is decided can never satisfy it, and — worse — it forces an honest
opponent to record a technical loss against a game it actually played.

**Why a bounded wait rather than "serve forever".** The opponent may legitimately never
audit: it may have crashed, or be a peer that does not implement the exchange. Waiting
forever converts their fault into our hang, and rule 6's watchdog exists precisely so no peer
freezes on another's silence. So the window is bounded by `audit_send_timeout_seconds` from
the private TOML — the same budget we allow ourselves for sending one — and its expiry is a
normal outcome, not an error: we return whether an audit arrived and let the caller record
that honestly.

**`confirmed` is what this changes.** Before this module the log hardcoded
`"confirmed": True`, which read as "the result was mutually agreed" while actually meaning
"negotiation succeeded". Those are different claims and only the second was ever true. The
artifact now asserts the first only when an opponent audit really arrived.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from p2p_thief_agent.adapters.artifact_writes import (
    RUNNING_COMMIT,
    log_context,
    write_pre_game_artifacts,
)

DEFAULT_AUDIT_WINDOW = 60.0
POLL_INTERVAL = 0.5
# Keep serving this long AFTER the audit lands, before exiting. Found 2026-08-12 against
# uoh-ay26: we received and verified their audit every time (confirmed:true), but exited
# within ~0.5s -- and their client, over a Tel-Aviv->Cloudflare->them tunnel, was still
# closing its session / retrying. That tail hit our already-dead origin as a 502, and they
# scored the sub-game a technical loss. The audit is mutual; the exchange is not over the
# instant we have what WE need. Draining continues through the grace, so a duplicate or a
# late follow-up is absorbed rather than refused.
AUDIT_GRACE_SECONDS = 12.0


def audit_window_seconds(private: Mapping[str, object] | None,
                         default: float = DEFAULT_AUDIT_WINDOW) -> float:
    """Read `[network].audit_send_timeout_seconds`, the budget for one audit exchange."""
    network = private.get("network") if isinstance(private, Mapping) else None
    value = network.get("audit_send_timeout_seconds") if isinstance(network, Mapping) else None
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) \
        else float(default)


def await_opponent_audit(
    *,
    drain: Callable[[], Any],
    audits_seen: Callable[[], int],
    clock: Callable[[], float],
    sleep: Callable[[float], None],
    timeout: float,
    poll_interval: float = POLL_INTERVAL,
    grace: float = AUDIT_GRACE_SECONDS,
) -> bool:
    """Wait up to `timeout` for the opponent's audit; once it lands, linger `grace` more.

    Returns whether one arrived. `drain` is injected rather than the inboxes themselves so a
    test can drive this without a socket — the same injection `readiness` and the watchdog
    use. The count is read through `audits_seen` for the same reason.

    The grace is the fix for the teardown race: exiting the instant we have the audit leaves
    the opponent's client hitting a dead origin (502) while it finishes its side of the
    exchange over a tunnel. We keep draining through the grace so a duplicate or a late
    follow-up is absorbed, then return. The grace stays well inside the watchdog budget.
    """
    if timeout <= 0:
        drain()
        return audits_seen() > 0
    deadline = clock() + timeout
    received_at: float | None = None
    while True:
        drain()
        if received_at is None and audits_seen() > 0:
            received_at = clock()
        now = clock()
        if received_at is not None:
            if now >= received_at + grace:
                return True
            until = received_at + grace - now  # lingering for the teardown grace
        elif now >= deadline:
            return False
        else:
            until = deadline - now  # still waiting for the audit
        sleep(min(poll_interval, max(0.0, until)))


def finalise(
    *,
    inboxes: Any,
    artifacts_dir: Any,
    records: list,
    result: Any,
    agreement: Any,
    game_config: Mapping[str, object] | None,
    identity: Mapping[str, object] | None,
    sub_game: int,
    started_at: object,
    audit_window: float,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
    write_log: Callable[..., Any],
    series_game_id: str,
) -> bool:
    """Hold the door open for the audit, then write the log. Returns whether one arrived.

    Kept here rather than in `serve.py` for the `G-04` length gate, but the grouping is
    honest on its own: everything after the last move belongs to the same phase.
    """
    from p2p_thief_agent.adapters.fastmcp_server import drain
    from p2p_thief_agent.adapters.opponent_audit import retain_opponent_audit
    from p2p_thief_agent.peer.inbound import InboundPeer

    audit_peer = InboundPeer()
    audited = await_opponent_audit(
        drain=lambda: drain(inboxes, audit_peer),
        audits_seen=lambda: len(audit_peer.audits_verified),
        clock=clock, sleep=sleep, timeout=audit_window,
    )
    print(f"opponent audit {'received' if audited else 'did not arrive in the window'}")
    if artifacts_dir is None:
        return audited
    context = None
    if agreement is not None and game_config is not None and identity is not None:
        from p2p_thief_agent.protocol.crypto import canonical_sha256
        from p2p_thief_agent.protocol.terms_projection import terms_from_shared_config
        from p2p_thief_agent.shared.series_identity import derive_game_uid, series_label

        sha = canonical_sha256(dict(game_config))
        # The agreed label names the files; the shared derivation names the set. Both are
        # computed here rather than defaulted, because a default is how this repository
        # and the companion drifted into two naming schemes for one G009 series.
        opponent_gid = str(agreement.peer_identity.get("group_id", "unknown"))
        context = log_context(
            sha=sha, sub_game=sub_game, identity=identity,
            opponent_group_id=agreement.peer_identity.get("group_id", "unknown"),
            started_at=started_at, confirmed=audited,
            opponent_commit=agreement.peer_identity.get("git_commit_hash", "unknown"),
            game_id=series_game_id,
            # The LABEL is threaded, not dropped. Without it this log carried the
            # unlabelled uid while the result carried the labelled one -- two names for
            # one series inside our own evidence (friendly-9).
            game_uid=derive_game_uid(
                terms_from_shared_config(dict(game_config)),
                [str(identity.get("group_id", "unknown")), opponent_gid],
                series_label(series_game_id,
                             [str(identity.get("group_id", "unknown")), opponent_gid]),
            ),
        )
    write_log(artifacts_dir, records, result, context)
    # Companion `C-051`: keep THEIR evidence, not just our verdict on it. `audit_peer` has
    # just verified every commitment in these payloads; discarding them left us unable to
    # say where their agent actually was, which is what a disputed capture claim turns on.
    retain_opponent_audit(
        artifacts_dir, game_id=series_game_id, sub_game=sub_game,
        audits=audit_peer.opponent_audits,
        opponent_group_id=str(agreement.peer_identity.get("group_id", ""))
        if agreement is not None else "",
    )
    if context is not None and agreement is not None and game_config is not None:
        # The log IS the game; the pre-game artifacts must never cost it. Found
        # live 2026-08-13: an opponent spec with foreign key names raised here
        # BEFORE the log was written, and sub-game 1 of a played, audited game
        # left no record on our side.
        try:
            write_pre_game_artifacts(
                artifacts_dir, context=context, identity=identity,
                peer_identity=agreement.peer_identity, game_config=game_config,
                started_at=str(started_at), github_commit=RUNNING_COMMIT,
            )
        except Exception as exc:  # noqa: BLE001 - artifacts are secondary evidence
            print(f"pre-game artifacts failed (log already written): {exc}")
    return audited
