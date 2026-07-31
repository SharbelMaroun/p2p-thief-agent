"""Accepted scoring and terminal-outcome calculation (Appendix F Table 17).

Every value here is an official FIXED score from the project book Appendix F Table 17
(`AF-017`), with tie and technical-loss semantics from Appendix E rule 19 (`AE-019`).
The module is pure: it names the fixed points and maps a terminal condition to a
result. It holds no Cop-private truth, performs no networking, and depends on no
shared-contract byte.

Scores are reported from the Thief's own perspective, because this is the Thief agent.
Table 17 fixes both role columns for capture, survival, and tie, so those public
constants are exposed too. Technical loss is **symmetric**, not asymmetric: chapter 3
table 2 (PDF p. 38) prints its row as `0 | 0` and Appendix E rule 48 writes it as
"technical loss 0/0", so both peers score zero whichever one falsified. This module
still reports only the Thief's own column because that is its role, not because the
counterpart value is unknown.
"""

from __future__ import annotations

from enum import Enum

from p2p_thief_agent.domain.coordinates import DomainError, _validate_index

# Appendix F Table 17 FIXED points (`AF-017`).
CAPTURE_COP = 20
CAPTURE_THIEF = 5
SURVIVAL_COP = 5
SURVIVAL_THIEF = 10
TIE_SCORE = 2
TECHNICAL_LOSS_SCORE = 0

# Appendix F Table 15 survival horizon (MINIMUM status, `AF-015`).
DEFAULT_SURVIVAL_THRESHOLD = 35


class Outcome(Enum):
    """The four terminal sub-game results (`AF-017`, `AE-019`)."""

    CAPTURE = "capture"
    SURVIVAL = "survival"
    TIE = "tie"
    TECHNICAL_LOSS = "technical_loss"


# The Thief's own points for each terminal outcome (`AF-017`, `AE-019`).
_THIEF_SCORES: dict[Outcome, int] = {
    Outcome.CAPTURE: CAPTURE_THIEF,
    Outcome.SURVIVAL: SURVIVAL_THIEF,
    Outcome.TIE: TIE_SCORE,
    Outcome.TECHNICAL_LOSS: TECHNICAL_LOSS_SCORE,
}


def thief_score(outcome: Outcome) -> int:
    """Return the Thief's own points for a terminal outcome."""
    if not isinstance(outcome, Outcome):
        raise DomainError(f"outcome must be an Outcome, got {type(outcome).__name__}")
    return _THIEF_SCORES[outcome]


# Simulator AuditPayload.result_claim vocabulary (capture / survival / timeout). The
# simulator groups timeout / tamper / stopped as the 0/0 technical-loss bucket, so a
# TECHNICAL_LOSS maps to "timeout" on the wire.
_WIRE_RESULT_CLAIM: dict[Outcome, str] = {
    Outcome.CAPTURE: "capture",
    Outcome.SURVIVAL: "survival",
    Outcome.TECHNICAL_LOSS: "timeout",
}


def wire_result_claim(outcome: Outcome) -> str:
    """Map a terminal Outcome to the simulator's AuditPayload.result_claim string.

    A TIE is decided only at series aggregation, never as a per-sub-game claim, so it
    has no wire result_claim.
    """
    if not isinstance(outcome, Outcome):
        raise DomainError(f"outcome must be an Outcome, got {type(outcome).__name__}")
    if outcome is Outcome.TIE:
        raise DomainError("a tie is a series-level result, not a sub-game result_claim")
    return _WIRE_RESULT_CLAIM[outcome]


def resolve_outcome(
    *,
    captured: bool,
    steps: int,
    survival_threshold: int = DEFAULT_SURVIVAL_THRESHOLD,
    technical_loss: bool = False,
) -> Outcome | None:
    """Classify a locally determinable terminal condition, or None if in progress.

    A technical loss overrides every other condition (`AE-019`). Otherwise a capture is
    terminal, and reaching the survival horizon is a survival. A tie is decided by the
    coordinator or mutual agreement rather than local capture state, so it is never
    inferred here; `thief_score(Outcome.TIE)` still scores it when it is declared.

    The horizon test is inclusive (`steps >= survival_threshold`): chapter 3 table 2
    defines survival as the Thief surviving "the limit of valid moves" without capture,
    and Appendix F table 15 sets `[Step Limit]` and `[Survival Threshold]` to the same
    value, so completing the final step uncaptured is a Thief win. Closes `U-022`.
    """
    _validate_index("steps", steps)
    _validate_index("survival_threshold", survival_threshold)
    if not isinstance(captured, bool):
        raise DomainError(f"captured must be a bool, got {type(captured).__name__}")
    if not isinstance(technical_loss, bool):
        raise DomainError(f"technical_loss must be a bool, got {type(technical_loss).__name__}")
    if steps < 0 or survival_threshold < 0:
        raise DomainError("steps and survival_threshold must be nonnegative")
    if technical_loss:
        return Outcome.TECHNICAL_LOSS
    if captured:
        return Outcome.CAPTURE
    if steps >= survival_threshold:
        return Outcome.SURVIVAL
    return None
