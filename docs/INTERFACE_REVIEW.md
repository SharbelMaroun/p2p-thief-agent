# Interface review — Nielsen's ten heuristics (`M8-004c`, `M8-011b`)

**Source of the requirement.** Asked directly, the *book* does not name Nielsen — that was
worth checking, because the row cites `[G§10.2]` and a rule that does not exist is the kind
of thing that gets defended in a viva. It comes from the **submission guidelines** §10.1,
which list the ten heuristics [ref 13/14], and §10.2, which asks for "screenshots of every
screen and state, a description of typical user workflows, explanations of interactions and
feedback, and accessibility considerations".

Reviewed against the two interfaces this repository actually ships: the **live GUI**
(`ui/live_app.py`) and the **replay viewer** (`ui/replay_app.py`).

| # | Heuristic | Live GUI | Replay viewer |
|---|---|---|---|
| 1 | Visibility of system status | Banner states the turn state in words *and* colour; step and score always on screen | Stamp shows the verdict; `step N of M` always visible |
| 2 | Match with the real world | `YOUR TURN` / `LOCKED`, not `PHASE_2`; `#` for a barrier, `T?`/`C?` for a guess | `Verified OK` / `TAMPERED` are the book's own words |
| 3 | User control and freedom | Move buttons are the only actions; nothing is destructive | Step back, restart, and jump — every navigation is reversible |
| 4 | Consistency and standards | Same palette, banner and legend in both windows | Same, deliberately |
| 5 | **Error prevention** | Buttons are **disabled** out of turn, and a click landing mid-repaint is dropped rather than queued | Cursor clamps at both ends instead of raising |
| 6 | Recognition over recall | A legend names every mark on screen; no key to memorise | Row list shows every step at once; the panel repeats the current one in full |
| 7 | Flexibility and efficiency | — *(see gap 1)* | `Jump to divergence` goes straight to the failing step |
| 8 | Aesthetic and minimalist design | Board, hints, legend, controls — nothing else | Verdict, records, detail, controls |
| 9 | **Recognise, diagnose, recover** | — *(see gap 2)* | The banner names the step *and* the reason; the panel shows the mismatching commit |
| 10 | Help and documentation | Legend line on screen; workflow in `PRD_gui.md` | Workflow and both states in `PRD_replay.md` |

## What is genuinely satisfied, and how it is checked

Heuristics 1, 2, 5, 6 and 9 are not claims — they are asserted in
`test_live_view_model.py` and `test_replay_view_model.py`: the banner text and colour per
state, the disabled-input rule, the legend contents, and the per-step reason line. A review
that only *asserted* compliance would be the kind of documentation §10.2 asks for and
nobody could verify.

**Accessibility (§10.2, and heuristic 1).** Colour is never the only signal in either
window: every believed cell prints its probability, the most likely cell is marked in text,
barriers carry `#` as well as a dark fill, and both verdicts are words before they are
colours. A greyscale print of either screenshot loses nothing.

## Gaps, stated rather than glossed

1. **Heuristic 7, live GUI — no keyboard path.** Moves are mouse-only. An operator playing
   a 35-turn sub-game clicks 35 times where four arrow keys would do. Not a rule violation
   and not fixed here; recorded because "flexibility and efficiency of use" is a heuristic
   we are claiming to have reviewed, and claiming a pass would be false.
2. **Heuristic 9, live GUI — no error surface.** The window has no place to *show* a
   protocol error. Today a refused turn appears only in the log, so the operator sees a
   board that has stopped moving and no reason. The replay viewer does this properly, which
   is what makes the live GUI's omission visible.
3. **Heuristic 3, both — no undo, by design.** A committed move is cryptographically bound
   (rule 17); offering to take it back would be offering to break the protocol. Listed as a
   deliberate non-implementation rather than an oversight.

Gaps 1 and 2 are interface polish, not correctness, and neither touches a sanctioned rule.
They are written down so the review is a review.
