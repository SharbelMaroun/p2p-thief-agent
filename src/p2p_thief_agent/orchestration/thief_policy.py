"""Turn this repository's policy into the turn loop's `decide` callable (`M9-026`).

The turn loop wants `(incoming, step) -> (public_message, sealed_record)`. Until now that
adapter existed **only in the tests**, which is why the CLI could not play a game: the policy
was finished, the loop was finished, and nothing in production joined them.

**Its home was decided by two tests, not by preference.** It seals, so it cannot live in
`strategy/` — `test_strategy_sdk.py` refuses a strategy module that imports `protocol`. It
reaches into the decision module, so it cannot live in `adapters/` either —
`test_orchestrator_boundary.py` refuses one subsystem importing another directly. Wiring
subsystems together is what `orchestration/` is for, and both tests said so before this file
existed anywhere else.
"""

from __future__ import annotations


def make_decide(*, grid_size: int = 7, start: tuple[int, int] = (3, 3)):
    """Build the turn-loop's `decide` callable from this policy (`M9-026`).

    The turn loop wants `(incoming, step) -> (public_message, sealed_record)`. Until now that
    adapter existed **only in the tests**, which is why the CLI could not play: the policy was
    finished and nothing in production turned it into a turn.

    It lives in `adapters/`, not `strategy/`, because it **seals** — and
    `test_strategy_sdk.py` refuses a strategy module that imports `protocol`. Putting it
    beside the policy would have been the obvious place and a layering violation; the
    test caught it immediately.

    State is closed over rather than global. Two matches in one process must not share a
    position, and rule 2 forbids sharing memory between parties at all — a module-level
    position would be the easiest possible way to violate it by accident.
    """
    from p2p_thief_agent.domain.board import Board  # noqa: PLC0415
    from p2p_thief_agent.domain.coordinates import Coordinate  # noqa: PLC0415
    from p2p_thief_agent.domain.movement import resolve_move  # noqa: PLC0415
    from p2p_thief_agent.protocol.crypto import seal  # noqa: PLC0415
    from p2p_thief_agent.strategy.baseline import choose_action  # noqa: PLC0415

    board = Board(size=grid_size)
    here = {"cell": Coordinate(*start)}

    def decide(incoming: dict | None, step: int) -> tuple[dict, dict]:
        action = choose_action(board, here["cell"])
        # `resolve_move` is what turns a direction into a cell, and it is the same
        # function `rank_actions` used to rank it — so the move played is the move that
        # was scored, rather than a second interpretation of the same enum.
        here["cell"] = resolve_move(board, here["cell"], action, frozenset())
        cell = here["cell"]
        payload = {
            "step": step,
            "state": f"grid={grid_size}x{grid_size};self=[{cell.row}, {cell.col}];barriers=[]",
            "position": [cell.row, cell.col],
            "move": f"MOVE:{getattr(action, 'name', 'STAY')}",
            # Truthful by default. Rule 22 punishes only the deliberate lie, and a bluffing
            # baseline would make every match harder to reason about for no measured gain.
            "verdict": "truth",
            "hint": "still running",
        }
        sealed = seal(payload)
        message = {"step": step, "sender": "thief", "hint": payload["hint"],
                   "smell_grid": {}, "commit": sealed["commit"], "timestamp": f"t{step}"}
        return message, {"payload": payload, **sealed}

    return decide
