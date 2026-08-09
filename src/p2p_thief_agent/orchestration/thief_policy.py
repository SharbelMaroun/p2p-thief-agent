"""Turn this repository's policy into the turn loop's `decide` callable (`M9-026`).

**Until 2026-08-07 this was the blind baseline wearing the live loop's clothes** — no
belief, no barriers, `incoming` ignored, an empty `smell_grid` (the rule-23 deviation),
no claim answers — while every measured result existed only in the harness (`M6-015c`).

What the live turn now does, in order:

1. **Absorb** the Cop's message (`orchestration/thief_absorb.py`): declared barriers
   accumulate (disclosure is a truth duty), and its `smell_grid` becomes a **model-matched
   belief** (`M6-031`) — the upgrade that took the pursuer grid from 23/8/5 escapes to
   **24/24/24 (240 league points)**. A cell off the board is *dropped*, not rejected
   (`M6-006b`, corrected 2026-08-09 after a matching defect lost the companion Cop
   repository's first friendly match). The prior survives silent or fully off-board turns.
2. **Answer a capture claim from the cell the claim was about** — the pre-move cell. The
   sub-game loop calls `answer_claim` *after* this turn's move is applied, so answering
   from live state would compare the claim against the cell we fled to and deny a true
   capture; the audit would then prove the denial false and rule `[AE-021]` scores a
   forgery zero for both sides. A confirmed capture also pins this turn's move to `STAY`.
3. **Evade** via `choose_adaptive_action` (`M6-030`) — classify the pursuer online, play
   the best-fit archetype's exact escape set, degrade to the shipped ranking when no
   model offers an escape. Measured dominant *with* the decoded belief and worse without
   it, which is why the two ship together or not at all.
4. **Emit involuntarily**: the own-trail field advances every turn and the wire carries
   the agreed 5×5 window of it.
5. **Claim survival** on the threshold step (`win_claim`), so the opponent records our
   survival instead of timing out into a disputed artifact.

It seals, so it cannot live in `strategy/`; it wires subsystems, which is what
`orchestration/` is for. State is closed over per factory call (rule 2: no shared memory
between parties).
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
    ``answer_claim`` so `serve_match` can pass both from one shared closure.
    `cop_start` sharpens the first belief to the public opening cell (`M6-021`);
    `threshold` is the negotiated horizon, carried into the planner and the
    survival `win_claim`.
    """
    from p2p_thief_agent.domain.board import Board  # noqa: PLC0415
    from p2p_thief_agent.domain.coordinates import Action, Coordinate  # noqa: PLC0415
    from p2p_thief_agent.domain.movement import resolve_move  # noqa: PLC0415
    from p2p_thief_agent.orchestration.thief_absorb import absorb_observation  # noqa: PLC0415
    from p2p_thief_agent.perception.belief import uniform_belief  # noqa: PLC0415
    from p2p_thief_agent.perception.field import blank_field, deposit  # noqa: PLC0415
    from p2p_thief_agent.perception.observation import encode_smell_grid  # noqa: PLC0415
    from p2p_thief_agent.protocol.sealing import (  # noqa: PLC0415
        StepDecision,
        build_turn_message,
        sealed_step_record,
    )
    from p2p_thief_agent.strategy.adaptive_policy import (  # noqa: PLC0415
        PursuerTracker,
        choose_adaptive_action,
    )
    from p2p_thief_agent.strategy.belief_policy import (  # noqa: PLC0415
        believed_cop_cell,
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
        "tracker": PursuerTracker(threshold if threshold is not None else 35),
        "seen": None,  # (step, observed cells) — the decoder's previous observation
        "dropped_off_board": 0,  # running total — visibility for M6-006b, see below
    }

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
            absorb_observation(state, incoming, step, board)
        claim = _claim_cell(incoming)
        caught = claim == [state["cell"].row, state["cell"].col] if claim else False
        if claim is not None:
            state["answered"] = (claim, caught)

        blocked = frozenset(state["barriers"])
        # A caught Thief seals the caught cell; and — the `M6-033` fail-safe — a
        # strategy exception must cost one imperfect turn, never the match: an
        # uncaught raise here reaches the watchdog as a freeze and scores the
        # technical 0/0, strictly worse than any legal move. STAY is legal from
        # every on-board cell and keeps the sealed record truthful.
        try:
            action = Action.STAY if caught else choose_adaptive_action(
                board, state["cell"], state["belief"], state["tracker"], step, blocked)
        except Exception:  # noqa: BLE001 - the match outlives any strategy bug
            action = Action.STAY
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
    # Visibility for the M6-006b fix: the running count of off-board cells dropped from
    # inbound smell_grids, so a caller (a log line, a test, an operator console) can tell
    # a normal edge-of-board window from a genuinely wrong-shaped opponent field, rather
    # than both looking identical from the outside.
    decide.dropped_off_board = lambda: state["dropped_off_board"]
    # Also exposed for the same reason `answer_claim` is: the chosen *action* is a coarse,
    # five-valued projection of belief, and two genuinely different beliefs can legitimately
    # collapse to the same best action (a Cop one cell away from another candidate rarely
    # changes which direction is furthest from both). A test or operator asking "is belief
    # actually tracking the opponent" needs the belief itself, not its lossy shadow.
    decide.believed_cop_cell = lambda: believed_cop_cell(state["belief"], board)
    return decide
