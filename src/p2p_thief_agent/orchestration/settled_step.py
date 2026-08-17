"""Which turn number a sub-game ended on, in the numbering of the side that caused it.

Agreed with `yanell11` on 2026-08-17, after our two `steps` fields disagreed on the same six
sub-games -- theirs 28 where ours said 29 -- and neither was wrong. Each side was reporting
its own move counter, and those were never the same quantity: the book only qualifies a turn
as *full* when it means both sides ("after both the cop and the thief have completed their
move"), so an unqualified step is one agent's move. The fix was not to pick a number but to
name whose counter:

    steps = the number of the turn on which the terminal condition occurred, in the
            numbering of the side that CAUSED it -- the Cop's turn for a capture, the
            Thief's for a survival. Operationally, the `step` field of the sealed record in
            which the terminal condition first appears.

This peer is always the Thief, which puts the two cases on opposite sides:

* a **capture** is caused by the opponent, so it settles on THEIR step -- read off the
  incoming message that carried the claim, not our own counter;
* a **survival** is caused by us, so it settles on our own threshold.

Our concession is a real sealed turn at the next step number, and it is real because the
opponent's peer refused it as a duplicate commitment three sub-games running on 08-15 -- one
commit per step. So the loser's counter always runs one past the winner's, which is exactly
the 29-against-28 we could not explain until the field was defined.
"""

from __future__ import annotations

from collections.abc import Mapping


def capture_step(received: object, our_step: int) -> int:
    """Return the opponent's step for a capture they caused, else our own.

    Falls back to our counter when their message carries no usable step: a number we can
    defend from our own artifacts beats an absent one, and the audit exchange lets either
    side recompute it from the same bytes afterwards.
    """
    if isinstance(received, Mapping):
        theirs = received.get("step")
        if isinstance(theirs, int) and not isinstance(theirs, bool) and theirs > 0:
            return theirs
    return our_step
