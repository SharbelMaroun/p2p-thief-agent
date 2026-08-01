"""Build and SHA-256-seal the records a peer commits to.

Independently authored to match the reference simulator's `peer/sealing.py`: the
per-step state payload, the step-0 host-spec declaration, and the public `TurnMessage`.
Inputs are explicit primitives (plain ``[row, col]`` lists, an already-chosen move),
so this stays independent of any runtime/config or domain object; the orchestration
layer supplies them from the Thief-local state. The sealed payload is this peer's own
truth: it is revealed and re-hashed at audit, so its field roster is our choice.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from p2p_thief_agent.protocol.crypto import seal
from p2p_thief_agent.protocol.wire import TurnMessage
from p2p_thief_agent.shared import __version__


class SealingError(ValueError):
    """Raised when a step-0 attestation is built without its mandatory bindings."""


@dataclass(frozen=True, slots=True)
class StepDecision:
    """One turn's private decision: the true move, the bluff verdict, and the hint."""

    move: str
    verdict: str
    hint: str
    prompt_text: str = ""
    reasoning: str = ""
    response_seconds: float = 0.0
    random_move: bool = False


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (book: mandatory per move)."""
    return datetime.now(UTC).isoformat()


def state_str(board_size: int, position: Sequence[int], barriers: Iterable[Sequence[int]]) -> str:
    """Return a compact, replayable board-state string for the sealed record."""
    ordered = sorted([list(cell) for cell in barriers])
    return f"grid={board_size}x{board_size};self={list(position)};barriers={ordered}"


def sealed_step_payload(
    *,
    step: int,
    board_size: int,
    position: Sequence[int],
    barriers: Iterable[Sequence[int]],
    decision: StepDecision,
    model: str = "unknown",
    tokens_step: int = 0,
    tokens_total: int = 0,
) -> dict:
    """Return one turn's full sealed payload (true state, move, verdict, hint, telemetry)."""
    return {
        "step": step,
        "state": state_str(board_size, position, barriers),
        "position": list(position),
        "move": decision.move,
        "intent": decision.verdict,
        "verdict": decision.verdict,
        "hint": decision.hint,
        "prompt_discussion": {
            "llm_prompt": decision.prompt_text,
            "llm_reasoning": decision.reasoning,
            "bluff_classification": decision.verdict,
        },
        "model": model,
        "tokens_step": tokens_step,
        "tokens_total": tokens_total,
        "response_seconds": decision.response_seconds,
        "random_move": decision.random_move,
    }


def sealed_step_record(**kwargs) -> dict:
    """Return {payload, nonce, commit} for one sealed turn (see sealed_step_payload)."""
    payload = sealed_step_payload(**kwargs)
    return {"payload": payload, **seal(payload)}


def sealed_spec_record(
    *,
    spec: dict,
    model: str,
    group_name: str,
    github_commit: str,
    token_budget: int,
    sub_game_number: int = 1,
    code_version: str = __version__,
) -> dict:
    """Return the sealed step-0 host-spec + identity declaration record.

    Beyond the reference simulator's step-0 fields (which this shares verbatim), this
    binds the **exact running Git commit** (`AE-53`) and the **agreed LLM token budget**
    (`AE-54`) into the sealed payload. Both are fixed before the first move and, being
    inside the commitment, cannot be revised afterwards. They fail closed: an absent
    commit or a nonsensical budget would make the per-game commit/token accounting
    meaningless, so this refuses rather than sealing a hollow attestation.
    """
    if not github_commit:
        raise SealingError("github_commit is required for the step-0 attestation (AE-53)")
    if isinstance(token_budget, bool) or not isinstance(token_budget, int) or token_budget < 0:
        raise SealingError(
            f"token_budget must be a non-negative integer, got {token_budget!r}"
        )
    payload = {
        "step": 0,
        "type": "system_spec",
        "spec": spec,
        "model": model,
        "code_version": code_version,
        "github_commit": github_commit,
        "token_budget": token_budget,
        "group_name": group_name,
        "sub_game_number": sub_game_number,
    }
    return {"payload": payload, **seal(payload)}


def build_turn_message(
    *,
    step: int,
    sender: str,
    hint: str,
    smell_grid: dict,
    commit: str,
    barrier_placed: list | None = None,
    capture_claim: list | None = None,
    claim_response: dict | None = None,
    win_claim: dict | None = None,
) -> TurnMessage:
    """Return the public TurnMessage for this turn (the turn token travels with it)."""
    return TurnMessage(
        step=step,
        sender=sender,
        hint=hint,
        smell_grid=smell_grid,
        commit=commit,
        timestamp=now_iso(),
        barrier_placed=barrier_placed,
        capture_claim=capture_claim,
        claim_response=claim_response,
        win_claim=win_claim,
    )
