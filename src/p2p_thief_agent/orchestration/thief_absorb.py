"""Absorb one inbound Cop turn into belief and barrier state (`M6-031`, `M6-006b`).

Split out of `thief_policy.py` to keep that module under the file-length gate; this is a
genuinely separable concern (perception/belief absorption) from turn orchestration (claim
answering, hint generation, message sealing).
"""

from __future__ import annotations

from contextlib import suppress

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.perception.belief import apply_evidence, uniform_belief
from p2p_thief_agent.perception.emitter_decoder import emitter_likelihood
from p2p_thief_agent.perception.observation import (
    ObservationError,
    parse_smell_grid,
    parse_smell_grid_dropped_count,
)


def absorb_observation(state: dict, incoming: dict, step: int, board: Board) -> None:
    """Fold one inbound Cop turn's barrier disclosure and `smell_grid` into `state`.

    Mutates ``state["barriers"]``, ``state["belief"]``, ``state["seen"]``, and
    ``state["dropped_off_board"]`` in place -- ``state`` is the same dict `make_decide`
    closes over, so nothing here needs to return anything.
    """
    placed = incoming.get("barrier_placed")
    if isinstance(placed, (list, tuple)) and len(placed) == 2:
        # A malformed disclosure is ignored, not fatal -- our moves must stay legal.
        with suppress(TypeError, ValueError):
            state["barriers"].add(Coordinate(int(placed[0]), int(placed[1])))
    raw = incoming.get("smell_grid") or {}
    try:
        # `M6-006b`, corrected 2026-08-09: a fixed-size window from a peer near an edge
        # or corner necessarily carries an off-board cell under this repo's absolute-
        # coordinate convention -- that used to reject the WHOLE grid and freeze belief
        # for the rest of the match against any such peer (reproduced against the
        # companion Cop repository's matching defect, which lost a friendly the same
        # day). `parse_smell_grid` now drops only the impossible cells; the count is
        # kept visible here rather than in a log nobody reads, so a grid that is mostly
        # or entirely off-board -- a real encoding mismatch, not just an edge window --
        # stays observable instead of degenerating silently into "no evidence" the way a
        # genuinely malformed message does below.
        observed = parse_smell_grid(raw, board)
        state["dropped_off_board"] += parse_smell_grid_dropped_count(raw, board)
    except ObservationError:
        observed = {}
    if observed:
        # `M6-031`: invert the locked physics rather than weighting raw intensity. The
        # residual against last turn's observation IS the newest stamp, and the window
        # is partial, so scoring trusts only cells both windows covered.
        before = state["seen"][1] if state["seen"] and state["seen"][0] == step - 1 else None
        trusted = set(observed) & set(before) if before else None
        state["belief"] = apply_evidence(
            uniform_belief(board.size, board.size),
            emitter_likelihood(board, observed, before, trusted))
        state["seen"] = (step, observed)
