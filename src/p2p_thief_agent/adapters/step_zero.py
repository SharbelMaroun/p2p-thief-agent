"""Assemble the sealed step-0 `system_spec` attestation the audit must carry (`AE-24`).

**Why this exists.** Confirmed with group `uoh-ay26` on 2026-08-12: a peer's
`AuditPayload.records` must begin with a step-0 `system_spec` record -- host spec, model,
running commit, token budget -- which the opponent unconditionally re-verifies, while the
saved game log deliberately excludes it. We already built that record (`sealed_spec_record`,
rule 24), but never attached it to a live audit, so every cross-team audit was rejected "at
steps [0]". Two of our own peers agreed with each other only because neither *sent* nor
*required* it.

The record is self-consistent commit-reveal (`SHA256(canonical_json(payload)+"|"+nonce)`), so
the opponent's verifier accepts it by re-hashing -- it never compares our spec to theirs.
What rule 24 does require is that the values be *honest*: the real running commit and the
agreed per-game token budget, both sealed before move one so neither can be revised after.

Kept out of `serve.py`, which sits one line under the 150-line gate.
"""

from __future__ import annotations

from collections.abc import Mapping

DEFAULT_COMMIT = "unknown"


def build_step_zero(identity: Mapping[str, object] | None,
                    game_config: Mapping[str, object] | None,
                    sub_game: int) -> dict | None:
    """Return the sealed step-0 record, or ``None`` if it cannot be built.

    Never raises: a missing identity/config or a spec problem returns ``None`` rather than
    blocking the match from starting. The caller simply omits the record, which is the old
    (rejected-by-strict-peers) behaviour -- strictly no worse than before this fix.
    """
    if identity is None or game_config is None:
        return None
    try:
        return _sealed(identity, game_config, sub_game)
    except Exception:  # noqa: BLE001 - a friendly must not fail to start over the attestation
        return None


def _sealed(identity: Mapping[str, object], game_config: Mapping[str, object],
            sub_game: int) -> dict:
    from p2p_thief_agent.protocol.sealing import sealed_spec_record  # noqa: PLC0415

    ident = identity if isinstance(identity, Mapping) else {}
    spec = ident.get("spec")
    return sealed_spec_record(
        spec=dict(spec) if isinstance(spec, Mapping) else {},
        model=str(ident.get("llm_model") or "unknown"),
        group_name=str(ident.get("group_name") or ident.get("group_id") or "unknown"),
        github_commit=_commit(),
        token_budget=_per_game_token_budget(game_config),
        sub_game_number=int(sub_game),
    )


def _commit() -> str:
    """The exact running commit, or the honest placeholder if git is unavailable.

    `describe_provenance` raises rather than inventing a value; a match must not fail to
    start because the working tree is a tarball, so a failure degrades to the placeholder
    here (the record still re-verifies -- only the fairness-bonus evidence is weaker)."""
    from p2p_thief_agent.reporting.provenance import describe_provenance  # noqa: PLC0415

    try:
        return str(describe_provenance().get("github_commit") or DEFAULT_COMMIT)
    except Exception:  # noqa: BLE001 - provenance must never block a match from starting
        return DEFAULT_COMMIT


def _per_game_token_budget(game_config: Mapping[str, object] | None) -> int:
    """The agreed series budget divided across its games (`AE-54`), never negative."""
    league = game_config.get("network_and_league") if isinstance(game_config, Mapping) else None
    if not isinstance(league, Mapping):
        return 0
    try:
        total = int(league.get("token_budget_per_series", 0))
        games = int(league.get("num_games", 1)) or 1
        return max(0, total // games)
    except (TypeError, ValueError):
        return 0
