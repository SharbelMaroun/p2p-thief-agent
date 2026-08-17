"""Reading the opponent's Step-0 attestation out of the audit they disclosed to us.

Rule 53 wants a commit per game per team. This side filed the opponent's as `"unknown"` on
every sub-game it played while the value sat in the first record of every audit they
revealed -- the same defect the companion Cop had, fixed there first and left here, which is
how one team ends up with two behaviours again.

Both key shapes are accepted. Our own two repositories sealed the commit differently until
2026-08-17 -- this side at top level as `github_commit`, the companion nested under
`code.git_commit` -- so a peer who took either as the convention must stay readable. Tighten
what you emit, keep what you accept broad.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

STEP_ZERO_TYPE = "system_spec"


def opponent_step_zero(audits: Sequence[Mapping[str, object]]) -> dict:
    """Return the opponent's Step-0 attestation payload, or an empty mapping."""
    for envelope in audits or ():
        if not isinstance(envelope, Mapping):
            continue
        for record in (envelope.get("records") or ()):
            payload = record.get("payload") if isinstance(record, Mapping) else None
            if not isinstance(payload, Mapping):
                continue
            if payload.get("type") == STEP_ZERO_TYPE or payload.get("step") == 0:
                return dict(payload)
    return {}


def opponent_commit(audits: Sequence[Mapping[str, object]]) -> str | None:
    """Return the commit the opponent attested to at Step 0, else None.

    None rather than a placeholder, so the caller decides what an absent attestation is
    called and "they did not disclose it" stays distinct from "we did not look".
    """
    payload = opponent_step_zero(audits)
    nested = payload.get("code")
    for candidate in (payload.get("github_commit"),
                      nested.get("git_commit") if isinstance(nested, Mapping) else None):
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None
