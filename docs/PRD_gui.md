# PRD — Live GUI

Status: confirmed future deliverable; no M1 implementation.

## Confirmed boundary

Appendix E rules 8–9 (`AE-008`) require a live UI that displays local truth only and
never exposes the complete objective board or the opponent's private state. `PS-007`
requires the UI to delegate through the SDK.

## Future acceptance criteria

- The Thief view shows only Thief-local state, received public data, and the
  Thief-maintained belief about the Cop.
- No UI adapter imports Cop runtime code or reads Cop storage.
- Every displayed field has a documented local/public provenance.
- The UI contains no game, strategy, protocol, or verification business logic.
- A truth-boundary test fails if objective opponent state reaches the view model.

Framework, layout, accessibility implementation, refresh timing, and screenshots are
team decisions for a later gate. ADR-0009 records the truth-model decision.

## The live GUI (`M8-001`, `M8-001d`)

Built. `ui/live_app.py` is the window; `live/local_truth.py` and `live/view_model.py` are
what it reads.

**Screens and states (`M8-011a`).** One screen. A banner across the top in one of four
states, the board beneath it, received hints beside it, a legend, and five move buttons.

| Banner | Colour | Means | Input |
|---|---|---|---|
| `YOUR TURN` | green `#2ecc71` | turn received (act enabled) | accepted |
| `LOCKED` | grey `#95a5a6` | commit sent (input locked) | **ignored** |
| `WAITING` | grey `#95a5a6` | awaiting the opponent's turn | ignored |
| `GAME OVER` | slate `#546e7a` | the sub-game has ended | ignored |

The first two are Figure 9's, labels included. Locking is mandatory rather than advisory —
asked directly, the interface "enforces the lock" after the commit to stop both sides acting
on one turn — so the buttons are genuinely disabled and a click that lands during the
repaint is dropped rather than queued. A queued move would surface a turn later as an action
nobody chose.

**What it may never show.** Rule 8 (Mandatory): "display true local information only",
sanction "disqualification due to data breach". Rule 9 (Prohibited): "do not display the
full objective board state", sanction **project disqualification**. Enforced by the type,
not by care: `LocalTruth`'s field set is closed and built from explicit keyword arguments,
so there is nowhere to put the opponent's position and no runtime object to read it from.
`test_local_truth_boundary.py` fails if a field is added or if the package imports anything
that knows an objective coordinate.

The `C?` mark is our own inference from scent, not a reported position — the distinction
the whole trust map rests on.

**Accessibility (`M8-011b`).** Colour is not the only signal: every believed cell prints
its probability, the most likely is marked in text, barriers carry `#` as well as a dark
fill, and the legend names each mark. Below one percent the label degrades to `<1%` rather
than rounding to `0%`, which would print a board claiming the opponent is nowhere.

**Barriers (`M8-007a`).** Rule 15 makes a barrier public *once declared*, so
`disclosed_barriers` is the snapshot's own input — an undeclared barrier is not filtered
out of the view, it never enters it. A barrier also outranks the heat beneath it, because
an operator who cannot see one will plan a move into it.
