# PRD — Replay and Verification

Status: **requirements settled 2026-08-06; implementation still pending (`M8-002` and its
family are PENDING).** The blocking questions this document previously listed as open —
canonicalization authority and which hash construction governs — are now answered.

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
  the log**", so a rewritten displayed move is a replay of a game nobody played.
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
