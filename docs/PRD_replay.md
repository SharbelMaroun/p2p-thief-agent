# PRD — Replay and Verification

Status: **verifier built 2026-08-06 and proven on foreign logs** (`M8-002a`–`d`, `M8-008`,
`M8-008a`/`c`/`d`, `M8-012`, `M8-012a`/`b` DONE). The replay **UI** (`M8-002`, `M8-002e`,
`M8-008b`) and the submission screenshots (`M8-015b`/`c`) remain open.

`src/p2p_thief_agent/replay/` — `load.py`, `verify.py`, `sequence.py`, `cursor.py` — at 100%
branch coverage, re-authored against this repository's own `protocol.crypto` (`THIEF-002`).

Appendix E rule 20 (`AE-020`) requires a replay application that reconstructs and verifies
a game. Confirmed with the book notebook 2026-08-06, quoting p. 129/272: the sanction is a
"**Threshold condition** for confirmation of logs and submission of the project" — the
project cannot be accepted without it, which makes this the highest-consequence row left in
this repository. Rules 17–19 (`AE-017`) make any hash mismatch a technical loss worth zero.

## Settled requirements

- **Exactly two verdicts.** `:1693` — a green `Verified OK` stamp, or a red `TAMPERED`
  banner after which "the replay is immediately invalidated". `:1769` adds "no appeal
  process and no room for manual correction", so a third or intermediate state is a state
  the rules do not have.
- **One bad step voids the whole match.** The book's own `replay` loop returns `TAMPERED`
  on the first failure (`:1743`), and `:1753`: "If any single step returns `TAMPERED`, the
  entire match is invalidated." Scoping a verdict to one step would understate the sanction.
- **The opponent's log must verify too (`M8-012a`).** Rule 36 mandates a "comprehensive
  mutual log audit" at the end of every match as a necessary condition for agreement
  (p. 131/276); p. 39/102: "each side presents its full log … each side reconstructs the
  opponent's data through the revealed nonces". A verifier that only reads its own output
  confirms that this repository's writer agrees with its reader, which it always will.
- **The verdict is recomputed on every navigation (`M8-008a`)**, never cached at load.
  The `Verified OK` stamp is submission evidence, and evidence computed once and painted
  thereafter describes the past rather than the file.
- **An in-play log is refused, not accused.** Rule 18 requires a running log to carry no
  nonces; stamping it `TAMPERED` would accuse an honest peer of the one thing that carries
  no appeal. A peer who *never* reveals is a settlement question, not a forgery.

## Which hash construction (`M8-002d`, `C-016` reclassified RESOLVED)

Chapter 7's `verify_step` sketch computes `SHA256("{nonce}|{move}")`; this repository's
commit-reveal seals the canonical payload with the nonce. They never agree.

`C-016` recorded this as an open CONFLICT. It is not one: `:1757` footnotes the listing in
the book's own voice — "the sketch simplified the input for the sake of the illustration;
in practice the signature covers all components of the step — Intent, Move, State and Nonce
— as detailed in the protocol in Chapter 5". Chapter 5 governs; nothing is escalated and
nothing is disclosed. The required action is unchanged: build from `protocol/crypto.py`,
never from the ch. 7 sketch.

ADR-0006 and ADR-0003 no longer block replay work — the construction is this repository's
own, and foreign-shape tolerance replaces the need for a settled cross-repo schema version.

## Acceptance criteria

- Replay consumes the accepted official log/result structures rather than simulator
  private classes.
- Each verified step is bound to the captured transcript and accepted canonical bytes.
- A changed commitment, revealed payload, or nonce is detected deterministically —
  including in a log this repository did not write (`M8-012b`).
- A record whose *visible* fields contradict its sealed payload is `TAMPERED` even when the
  digest matches. `:1691` has the viewer re-encode "the Nonce and the move **appearing in
  the log**", so a rewritten displayed move is a replay of a game nobody played. **Built.**
- **Structural damage is reported, not bannered (`M8-008d`, `U-026`).** Shuffled, deleted and
  duplicated records survive every digest. `sequence.py` detects them and tags each finding
  with the rule it answers to — rule 35 for a gap or duplicate, rule 5 for a non-ascending
  order — while the `Verified OK` / `TAMPERED` stamp stays digest-only. Neither the book nor
  the reference requires ordering to be checked, so red-bannering an opponent over it would
  be a false accusation with no appeal (`:1769`), and rule 35 would score zero for both.
- A mismatch produces the official technical-loss outcome; it is never shown as "verified."
- The viewer reads through the SDK/verifier and contains no hashing business logic.
- Normal, malformed, missing, reordered, duplicate, and tampered records are all tested.

## Submission evidence

The `Verified OK` screenshot must appear **within the README.md academic report**
(p. 81/189), described there as "absolute mandatory". The exact filename and directory are
**not specified** by Appendix E or the submission checklist — a project choice, to be
recorded when `M8-015b` is built.

UI framework and navigation remain team choices. The reference simulator ships Tkinter with
`Play/Pause`, `Step >`, `Restart`, sub-game selection and `Go to step`.

## The view (`M8-002`, `M8-002e`)

Built. `ui/replay_app.py` is a Tk window; `replay/view_model.py` is what it reads.

**Screens and states.** One screen, two states. A stamp across the top — green
`Verified OK` or red `TAMPERED` — with the match banner beneath it, the source path, and
the sequence line. Below: every record with its own verdict, and a detail panel showing the
step under the cursor with its `nonce`, `move` and full `commit`, which is the set the book
requires (p.56/142). Controls are `|< Restart`, `< Back`, `Step >` and `Jump to divergence`,
covering "back and forth in time" (p.56/141).

**The board is deliberately absent.** Asked directly, it is not required — "the mandatory
screenshot requirement focuses on the verdict banner" — and the belief map belongs to the
live GUI, which is where the book puts it.

**No widget touches domain or protocol code** (`M8-006`). The view-model produces frozen,
display-ready values and the widgets read nothing else, so a widget cannot mutate a replay
and the screen's claims can be asserted in CI even though a Tk window cannot.

## Submission screenshots (`M8-015`)

`assets/replay-verified-ok.png` and `assets/replay-tampered.png`, regenerated by
`scripts/capture_replay_screenshots.py` from two committed fixtures.

Three things here are **project choices, not requirements**, and are recorded as such:

* the `assets/` location — the book "only mandates that the images be displayed within the
  README.md academic report" and does not mandate an `assets/` directory;
* the `TAMPERED` capture — only `Verified OK` is a mandatory submission image;
* showing our own log rather than an opponent's — the book does not say which.

They are real screen captures of the real widget tree. A rendered picture of what the app
would look like would satisfy the row and be a fabricated exhibit.
