"""C-037: a `boxed_in` claim must never end this peer's sub-game.

The companion Cop now *accepts* group `uoh-ay26`'s ``win_claim``
``{"type": "boxed_in"}`` from a Thief sender, because only a Thief can observe that
its own cardinal neighbours are all barriered or off-board, and conceding runs
against its own interest.

The mirror of that rule belongs here, and it is the opposite one. A Cop sending this
claim would be asserting *our* capture with no proof at all, which rule 22 makes a
disqualifying false declaration. ``_caught_by`` already refuses it -- it reads only
``capture_claim`` and checks it against our real cell -- but nothing pinned that, and
an unpinned guarantee is one refactor from being lost. `THIEF-002` forbids satisfying
a task here with the companion's work, so this repository states the rule itself.
"""

from p2p_thief_agent.orchestration.sub_game import _caught_by
from p2p_thief_agent.protocol.wire import TurnMessage


def turn(**extra: object) -> dict:
    """A wire-complete turn message from the opposing Cop."""
    return {"step": 7, "sender": "police", "hint": "cornered", "smell_grid": {},
            "commit": "a" * 64, "timestamp": "2026-08-12T00:00:00+00:00", **extra}


def at(row: int, col: int):
    """An ``answer_claim`` that is truthful about standing on ``(row, col)``."""
    return lambda claim: claim == [row, col]


def test_a_boxed_in_claim_alone_never_captures_us() -> None:
    """Rule 22: an unproven assertion of our capture is not believed."""
    assert _caught_by(turn(win_claim={"type": "boxed_in"}), at(3, 3)) is None


def test_a_survival_claim_from_the_cop_never_captures_us() -> None:
    """Neither terminal claim shape is a capture channel."""
    assert _caught_by(turn(win_claim={"type": "survival"}), at(3, 3)) is None


def test_a_boxed_in_claim_does_not_mask_a_real_capture_claim() -> None:
    """The extension must not change how a genuine, correct claim resolves."""
    message = turn(capture_claim=[3, 3], win_claim={"type": "boxed_in"})
    assert _caught_by(message, at(3, 3)) is not None


def test_an_incorrect_capture_claim_still_continues_the_game() -> None:
    """A claim is checked, never believed -- unchanged by the widening."""
    assert _caught_by(turn(capture_claim=[0, 0]), at(3, 3)) is None


def test_the_wire_model_tolerates_the_unknown_claim_shape() -> None:
    """Parsing must survive it, or the turn is lost before any rule applies.

    This side validates in code rather than against the shared bundle, so the
    guarantee is that ``win_claim`` is carried through uninterpreted.
    """
    message = TurnMessage.from_dict(turn(win_claim={"type": "boxed_in"}))
    assert message.win_claim == {"type": "boxed_in"}
    assert message.sender == "police"
