# counted-1 vs `yanell11` — this side's record

Filed 2026-08-17. `sharNamr-vs-yanell11-counted-1`, uid
`c7794f4c-325a-d005-74d0-7964090c098a`, **77–77**, both teams' reports reconciled on every
adjudicating field including the consensus digest
`f35c365326fa53e15ba2dffdb7a39e39c0739d233aefc8328efef80cd9819442`.

The full account of the nine series that preceded it lives in the companion Cop's
`docs/COUNTED_1_REPORT.md`, because the series report is a team artifact and only that side
assembles it. This page records what changed **here**.

## This side's result

Sub-games 2, 4 and 6, as Thief. Captured at step 28 in all three — their Cop builds a wall down
column 3, splits the board, then seals whichever pocket we are in. 5 points each to us, 20 to
them.

## What changed in this repository

**`open_field_v3`** — evasion that defends reachable space rather than distance. It flood-fills
the region reachable before the pursuer could cut it off, with barriers as walls, because a
barrier does not change how far away the Cop is: it changes how much board is left. Distance
cannot see a wall coming; this can. Adjacency is excluded outright — the Cop moves first in the
sub-games where it initiates the turn, so ending a turn beside it is a chosen capture, which is
exactly the STAY-at-distance-1 that lost run 4 four times over.

It survives both of the companion's Cops, where the previous two arms lose to each. **It still
loses to their column-3 partition**, and that is the honest strategic gap: it cannot see a
pocket with a narrow mouth. Region size says "plenty of room" right up until two barriers close
the door.

**The step rule.** A capture is caused by the opponent, so it settles on *their* claiming turn,
read off the incoming message rather than our own counter. Our concession is a real sealed turn
one step later — real because their peer refused it as a duplicate commitment three sub-games
running — so our counter always ran one past theirs. That is the 29-against-28 that disagreed
for four series, and naming whose counter was the fix rather than picking a number.

**The series label in the uid.** `derive_game_uid` gained the labelled branch, byte-compatible
with the companion's, because the two repositories name the artifacts of one series and a label
one side recognises and the other does not puts two uids on the same six sub-games. friendly-10
shipped exactly that.

**`cop_start` and the strategy selector.** Both silently broken. `cop_start` was never passed,
so the first belief was uniform over 49 cells while the signed terms published the Cop's opening
square. And the selector read a `policy` key while the config has always written `name`, so
nothing written in that file had any effect and `barrier_aware_v2` could not be switched on at
all. A flag that cannot be turned on is worse than one that does not exist, because it reads as
tested.

**The scent lock declared a model this peer does not run.** `settle()` had clamped tau to
[0, 0.9] for days while the locked record still declared the unbounded formula — and the
companion locked `c77a1260…` while this side answered `e6aef097…`, so one team declared two
models. The test that exists to catch a cross-peer split went on passing, because it recomputes
from this repository alone: a literal updated on one side records agreement instead of checking
it.

**The Step-0 reader read the wrong list.** `InboundPeer` keeps `audits_verified` (pass/fail
verdicts) beside `opponent_audits` (the disclosed payloads). We threaded the verdicts, so the
search for the opponent's commit ran over a list with no records in it and correctly found
nothing, filing `"unknown"` on every sub-game while their attestation sat in the list beside it.
Two names that both sound like the evidence.

## Open here

- The Thief loses to a partitioning Cop. Bottleneck-width scoring is the candidate fix, and it
  needs testing against a partitioner rather than against our own Cop — which is the mistake
  that made `open_field_v3` look sufficient.
- `scripts/experiment_yanell11_thief.py` carries two corrections worth keeping: it models the
  **Cop moving first** (modelling the Thief first makes every arm look invincible, because the
  Cop can then only land on a cell we have already left), and its pursuers tie-break by squared
  distance, because breaking Manhattan ties by `(row, col)` pins a chaser to row 0 forever.
