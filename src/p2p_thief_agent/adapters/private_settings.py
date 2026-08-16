"""Reading the Thief's own private settings, each with the same never-raise contract.

Split from `play_command.py` under the file-length gate. The three readers here share one
rule that is easier to state once than to repeat: **a config problem costs the setting,
never the match.** Each falls back to a documented default rather than propagating, because
an unreadable TOML at the top of a counted series must cost a worse timeout or a duller
strategy -- not a technical loss before move one.

They read the PRIVATE file, never the signed terms. Anything both peers agreed in writing
lives in `negotiated_terms`; the split is that boundary, not a line count.
"""

from __future__ import annotations

from pathlib import Path


def _audit_window(private: Path | None) -> float:
    """How long to stay reachable for the opponent's audit, from the private TOML.

    Never raises: a missing or unreadable private file falls back to the default window
    rather than refusing to play. The window is generous by design — see `post_match`.
    """
    from p2p_thief_agent.adapters.post_match import (  # noqa: PLC0415
        DEFAULT_AUDIT_WINDOW,
        audit_window_seconds,
    )

    if private is None:
        return DEFAULT_AUDIT_WINDOW
    try:
        from p2p_thief_agent.shared.private_config import load_private_config  # noqa: PLC0415

        return audit_window_seconds(load_private_config(private))
    except Exception:  # noqa: BLE001 - a config problem must not cost the audit window
        return DEFAULT_AUDIT_WINDOW


def _connect_budget(private: Path | None) -> float:
    """How long to wait for the opponent to answer, from the private TOML.

    The Cop has read ``[network].connect_timeout_seconds`` since M9; this side silently
    kept `serve_match`'s 30-second default, and that asymmetry ended the first amireman
    smoke at the role swap: their Police server was still rebinding for sub-game 2 when
    our 30 seconds ran out, and the whole series quit as "match did not start". Same
    never-raise contract as `_audit_window` — a config problem must not shrink the wait.
    """
    from p2p_thief_agent.services.readiness import (  # noqa: PLC0415
        DEFAULT_CONNECT_TIMEOUT,
        timeouts_from_private_config,
    )

    if private is None:
        return DEFAULT_CONNECT_TIMEOUT
    try:
        from p2p_thief_agent.shared.private_config import load_private_config  # noqa: PLC0415

        return timeouts_from_private_config(load_private_config(private))[0]
    except Exception:  # noqa: BLE001 - a config problem must not shrink the wait
        return DEFAULT_CONNECT_TIMEOUT


def _strategy(private: Path | None) -> dict:
    """Per-opponent strategy flags from the private TOML's ``[strategy]`` table.

    Private on purpose: these describe the OPPONENT's protocol profile (e.g. amireman's
    Cop claims its own cell every turn, so ``claim_reveals_cop`` turns that claim into
    pursuer intel), and never enter the signed terms. Same never-raise contract as the
    other private readers — a config problem costs the flag, not the match.

    **Two spellings for the policy selector, deliberately.** The shipped config has
    always written `name` (matching the companion Cop's `[strategy] name`), while the
    call site only ever read `policy` -- so the selector silently resolved to
    "current" whatever the file said, and `barrier_aware_v2` was unreachable through
    configuration. A flag that cannot be switched on is worse than one that does not
    exist, because it reads as tested. Both keys are accepted rather than renaming
    one, since the file on disk is what a live series runs with.
    """
    if private is None:
        return {}
    try:
        from p2p_thief_agent.shared.private_config import load_private_config  # noqa: PLC0415

        section = load_private_config(private).get("strategy")
        return dict(section) if isinstance(section, dict) else {}
    except Exception:  # noqa: BLE001 - a config problem must not cost the match
        return {}
