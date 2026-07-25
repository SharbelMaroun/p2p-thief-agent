# PRD — Replay and Verification

Status: confirmed future deliverable; canonicalization and artifact constraints pending.

Appendix E rule 20 (`AE-020`) requires a replay application that reconstructs and
verifies a game. Rules 17–19 (`AE-017`) require SHA-256 commit-reveal and make any hash
mismatch a technical loss worth zero.

## Future acceptance criteria

- Replay consumes the accepted official log/result structures rather than simulator
  private classes.
- Each verified step is bound to the captured transcript and accepted canonical bytes.
- A changed commitment, revealed payload, or nonce is detected deterministically.
- A mismatch produces the official technical-loss outcome; it is never shown as
  “verified.”
- The viewer reads through the SDK/verifier and contains no hashing business logic.
- Normal, malformed, missing, reordered, duplicate, and tampered records are tested
  only against proven schema constraints.

ADR-0006 must settle canonicalization and ADR-0003 must resolve compatible schema
versions before replay code begins. UI framework and navigation remain team choices.
