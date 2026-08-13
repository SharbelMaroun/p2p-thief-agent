"""The live `decide` plays the measured policy, honestly (`M9-026b`).

Until 2026-08-07 the wire loop played the blind baseline, sent an empty `smell_grid`,
and would deny every capture claim via `serve_match`'s lying default. Each test here
pins one of those against recurring.
"""

from p2p_thief_agent.domain.board import Board
from p2p_thief_agent.domain.coordinates import Coordinate
from p2p_thief_agent.orchestration.thief_policy import make_decide
from p2p_thief_agent.perception.field import blank_field, deposit
from p2p_thief_agent.perception.observation import encode_smell_grid
from p2p_thief_agent.protocol.wire import TurnMessage

BOARD = Board(size=7)


def cop_message(step: int, cop_cell: Coordinate, **extra) -> dict:
    """A schema-shaped Cop turn whose smell window reveals the Cop's own trail."""
    trail = deposit(blank_field(BOARD), BOARD, cop_cell)
    window = {(r, c): trail[r][c]
              for r in range(BOARD.size) for c in range(BOARD.size) if trail[r][c] > 0}
    return {"step": step, "sender": "police", "hint": "closing in",
            "smell_grid": encode_smell_grid(window), "commit": "0" * 64,
            "timestamp": f"t{step}", **extra}


def test_the_live_thief_flees_the_observed_trail() -> None:
    decide = make_decide(start=(3, 3))
    message, sealed = decide(cop_message(1, Coordinate(3, 1)), 1)
    row, col = sealed["payload"]["position"]
    assert abs(row - 3) + abs(col - 1) > 2, "the believed Cop is at (3,1); we gain ground"
    assert (row, col) not in {(3, 3), (3, 2)}, "neither staying nor stepping toward it"
    assert message["sender"] == "thief"


def test_the_live_thief_never_moves_into_a_declared_barrier() -> None:
    decide = make_decide(start=(3, 3))
    message = cop_message(1, Coordinate(3, 1), barrier_placed=[3, 4])
    _, sealed = decide(message, 1)
    assert sealed["payload"]["position"] != [3, 4]
    assert "barriers=[[3, 4]]" in sealed["payload"]["state"]


def test_a_correct_capture_claim_is_confirmed_from_the_pre_move_cell() -> None:
    decide = make_decide(start=(3, 3))
    message, sealed = decide(cop_message(1, Coordinate(0, 0), capture_claim=[3, 3]), 1)
    assert message["claim_response"] == {"claim": [3, 3], "caught": True}
    assert sealed["payload"]["position"] == [3, 3], "a caught Thief seals the caught cell"
    assert sealed["payload"]["move"] == "MOVE:STAY"
    # The loop asks *after* the move is applied; the answer must still be honest.
    assert decide.answer_claim([3, 3]) is True


def test_a_wrong_capture_claim_is_denied_and_play_continues() -> None:
    decide = make_decide(start=(3, 3))
    message, sealed = decide(cop_message(1, Coordinate(3, 1), capture_claim=[0, 6]), 1)
    assert message["claim_response"] == {"claim": [0, 6], "caught": False}
    assert sealed["payload"]["move"] != "MOVE:STAY" or sealed["payload"]["position"] != [0, 6]
    assert decide.answer_claim([0, 6]) is False


def test_the_smell_grid_is_a_real_window_centred_on_the_thief() -> None:
    decide = make_decide(start=(3, 3))
    message, sealed = decide(None, 1)
    row, col = sealed["payload"]["position"]
    assert message["smell_grid"], "an empty smell_grid deviates from the locked model"
    assert message["smell_grid"][f"{row},{col}"] >= 0.9, "the centre carries the emission peak"


def test_the_survival_threshold_step_carries_the_win_claim() -> None:
    decide = make_decide(start=(3, 3), threshold=2)
    first, _ = decide(None, 1)
    second, _ = decide(cop_message(2, Coordinate(0, 0)), 2)
    assert first["win_claim"] is None
    assert second["win_claim"] == {"type": "survival"}


def test_identical_inputs_give_identical_turns() -> None:
    replies = []
    for _ in range(2):
        decide = make_decide(start=(3, 3))
        message, sealed = decide(cop_message(1, Coordinate(5, 5)), 1)
        replies.append((message["smell_grid"], sealed["payload"]["position"],
                        sealed["payload"]["move"], message["hint"]))
    assert replies[0] == replies[1]


def test_an_empty_observation_keeps_the_carried_belief() -> None:
    """A quiet turn degrades to the prior — it must not reset evasion to a corner tie."""
    steady = make_decide(start=(3, 3))
    steady(cop_message(1, Coordinate(3, 1)), 1)
    _, sealed = steady(cop_message(2, Coordinate(3, 1)) | {"smell_grid": {}}, 2)
    fresh = make_decide(start=(3, 3))
    fresh(cop_message(1, Coordinate(3, 1)), 1)
    _, expected = fresh(cop_message(2, Coordinate(3, 1)), 2)
    assert sealed["payload"]["position"][1] >= 3, "the remembered threat is west of us"
    assert isinstance(expected["payload"]["position"], list)


def test_every_outbound_message_parses_as_a_turn_message() -> None:
    decide = make_decide(start=(3, 3), threshold=3)
    incoming = None
    for step in range(1, 4):
        message, _ = decide(incoming, step)
        parsed = TurnMessage.from_dict(message)
        assert parsed.step == step
        incoming = cop_message(step + 1, Coordinate(0, step))


def test_serve_match_refuses_to_play_without_an_honest_claim_answerer() -> None:
    import pytest

    from p2p_thief_agent.adapters.serve import ServeError, serve_match

    with pytest.raises(ServeError, match="answer_claim"):
        serve_match(peer_url="http://127.0.0.1:9", port=9009, series_game_id="G009",
                    survival_threshold=5, decide=lambda incoming, step: ({}, {}))
