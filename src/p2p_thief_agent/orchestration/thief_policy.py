"""Turn this repository's policy into the turn loop's `decide` callable (`M9-026`).

**Until 2026-08-07 this was the blind baseline wearing the live loop's clothes.** It
called `baseline.choose_action` with no threats and no barriers, ignored the Cop's
message entirely, sent a hard-coded empty `smell_grid`, and never answered a capture
claim. Every M6 result — the belief, the evasion that scores 235 against 175, the
involuntary emission — existed only in the harness while the wire played something
measurably worse than a random walk (`M6-015c`), and an empty `smell_grid` after
hash-locking an emission model is precisely the rule-23 deviation the companion peer
fixed on its own side.

What the live turn now does, in order:

1. **Absorb** the Cop's message: declared barriers accumulate (`barrier_placed` is
   trusted — rule: barriers are disclosed truthfully), and its `smell_grid` rebuilds
   the belief fresh — the prior carried only across empty or malformed observations,
   never compounded into them, which is what the measured harness arm does and what
   keeps the argmax tracking a moving emitter instead of calcifying on its history.
2. **Answer a capture claim from the cell the claim was about** — the pre-move cell.
   The sub-game loop calls `answer_claim` *after* this turn's move is applied, so
   answering from live state would compare the claim against the cell we fled to and
   deny a true capture; the audit would then prove the denial false and rule `[AE-021]`
   scores a forgery zero for both sides. A confirmed capture also pins this turn's
   move to `STAY`: the sealed record must show us on the cell we were caught on.
3. **Evade** via `choose_evasive_action` — the measured policy, aimed at the belief,
   around the disclosed barriers.
4. **Emit involuntarily**: the own-trail field advances every turn (`deposit` takes
   the cell, never the action) and the wire carries the 5×5 window around us, exactly
   as the emission model locked at negotiation says it must.
5. **Claim survival** on the threshold step (`win_claim`), so the opponent terminates
   with our survival on its record instead of timing out into a disputed artifact.

Home and layering are unchanged: it seals, so it cannot live in `strategy/`
(`test_strategy_sdk.py`), and it wires subsystems, which is what `orchestration/` is
for. State is closed over per factory call — two matches must not share a position,
and rule 2 forbids sharing memory between parties at all.
"""

from __future__ import annotations

from contextlib import suppress

_WINDOW_RADIUS = 2  # the agreed 5×5 smell window reaches two cells from its centre


def make_decide(
    *,
    grid_size: int = 7,
    start: tuple[int, int] = (3, 3),
    cop_start: tuple[int, int] | None = None,
    threshold: int | None = None,
):
    """Build the turn-loop `decide` callable from the measured evasion policy.

    The returned function carries its honest claim-answerer as the attribute
    ``answer_claim`` so `serve_match` can pass both from one shared closure — a
    separate default that always denies would be a standing lie the audit exposes.

    `cop_start` sharpens the first turn's belief to the public opening cell
    (`M6-021`); without it the first belief is honestly uniform. `threshold` is the
    negotiated survival horizon; when given, the message for that step carries the
    survival `win_claim` the book gives this side to declare.
    """
    from p2p_thief_agent.domain.board import Board  # noqa: PLC0415
    from p2p_thief_agent.domain.coordinates import Action, Coordinate  # noqa: PLC0415
    from p2p_thief_agent.domain.movement import resolve_move  # noqa: PLC0415
    from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief  # noqa: PLC0415
    from p2p_thief_agent.perception.field import (  # noqa: PLC0415
        blank_field,
        deposit,
        scent_likelihood,
    )
    from p2p_thief_agent.perception.observation import (  # noqa: PLC0415
        ObservationError,
        encode_smell_grid,
        parse_smell_grid,
    )
    from p2p_thief_agent.protocol.sealing import (  # noqa: PLC0415
        StepDecision,
        build_turn_message,
        sealed_step_record,
    )
    from p2p_thief_agent.strategy.belief_policy import (  # noqa: PLC0415
        choose_evasive_action,
        initial_belief,
    )
    from p2p_thief_agent.verbal.generation import generate_hint  # noqa: PLC0415

    board = Board(size=grid_size)
    state = {
        "cell": Coordinate(*start),
        "trail": blank_field(board),
        "barriers": set(),
        "belief": (initial_belief(board, Coordinate(*cop_start))
                   if cop_start is not None else uniform_belief(board.size, board.size)),
        "answered": None,  # (claimed [row, col], caught) for the loop's answer_claim
    }

    def _absorb(incoming: dict) -> None:
        placed = incoming.get("barrier_placed")
        if isinstance(placed, (list, tuple)) and len(placed) == 2:
            # A malformed disclosure is ignored, not fatal — our moves must stay legal.
            with suppress(TypeError, ValueError):
                state["barriers"].add(Coordinate(int(placed[0]), int(placed[1])))
        try:
            observed = parse_smell_grid(incoming.get("smell_grid") or {}, board)
        except ObservationError:
            observed = {}
        if observed:
            # Fresh each turn, not Bayes-recursive: recursion under this static
            # likelihood has no motion model, so history accumulates and the argmax
            # calcifies on old trail — the companion's opponent grid measured the
            # recursive form losing the target it tracks when rebuilt fresh. The
            # carried prior serves only silent turns, where it beats resetting to a
            # corner-tied uniform. This is also exactly what `M6-015`'s harness arm
            # measures, so the live Thief plays the policy the numbers are about.
            state["belief"] = apply_evidence(
                uniform_belief(board.size, board.size), scent_likelihood(observed, board))

    def _claim_cell(incoming: dict | None) -> list | None:
        claim = incoming.get("capture_claim") if isinstance(incoming, dict) else None
        if isinstance(claim, (list, tuple)) and len(claim) == 2:
            with suppress(TypeError, ValueError):
                return [int(claim[0]), int(claim[1])]
        return None

    def _window(cell) -> dict:
        base_r, base_c = cell.row - board.min_index, cell.col - board.min_index
        return {
            (board.min_index + r, board.min_index + c): state["trail"][r][c]
            for r in range(base_r - _WINDOW_RADIUS, base_r + _WINDOW_RADIUS + 1)
            for c in range(base_c - _WINDOW_RADIUS, base_c + _WINDOW_RADIUS + 1)
            if 0 <= r < board.size and 0 <= c < board.size
        }

    def decide(incoming: dict | None, step: int) -> tuple[dict, dict]:
        if isinstance(incoming, dict):
            _absorb(incoming)
        claim = _claim_cell(incoming)
        caught = claim == [state["cell"].row, state["cell"].col] if claim else False
        if claim is not None:
            state["answered"] = (claim, caught)

        blocked = frozenset(state["barriers"])
        if caught:
            action = Action.STAY  # the sealed record must show the cell we were caught on
        else:
            action = choose_evasive_action(board, state["cell"], state["belief"], blocked)
        state["cell"] = resolve_move(board, state["cell"], action, blocked)
        state["trail"] = deposit(state["trail"], board, state["cell"])

        hint = generate_hint(step, intent="truth")
        record = sealed_step_record(
            step=step, board_size=grid_size,
            position=[state["cell"].row, state["cell"].col],
            barriers=[[c.row, c.col]
                      for c in sorted(state["barriers"], key=lambda c: (c.row, c.col))],
            decision=StepDecision(move=f"MOVE:{action.name}", verdict="truth", hint=hint.text),
        )
        message = build_turn_message(
            step=step, sender="thief", hint=hint.text,
            smell_grid=encode_smell_grid(_window(state["cell"])),
            commit=record["commit"],
            claim_response={"claim": claim, "caught": caught} if claim is not None else None,
            win_claim={"type": "survival"} if threshold is not None and step >= threshold else None,
        ).to_dict()
        return message, record

    def answer_claim(claim: object) -> bool:
        """Answer from the cell the claim was made against, never the cell we fled to."""
        answered = state["answered"]
        normalised = list(claim) if isinstance(claim, (list, tuple)) else claim
        if answered is not None and answered[0] == normalised:
            return answered[1]
        return normalised == [state["cell"].row, state["cell"].col]

    decide.answer_claim = answer_claim
    return decide
