# PRD — Commit-Reveal

Status: mandatory mechanism confirmed; payload and canonicalization gate pending.

## Confirmed requirements

- Every protected move uses SHA-256 commit-reveal (`AE-017`).
- The nonce remains secret until the required end-of-game reveal.
- Audit recomputes commitments; any mismatch is a technical loss worth zero.
- A replay/verifier is mandatory (`AE-020`).
- The official logs visibly contain `payload`, `nonce`, and `commit` keys (`JS-001`),
  but populated examples do not prove all constraints.

## Still open

`U-002`, `U-004`, and `U-005` retain the exact canonical byte procedure, message
sequence/acknowledgement fields, committed field set, identity binding, signature
procedure, nonce encoding/length, and error envelope. ADR-0006 cannot be accepted until
the Cop proposal cites controlling evidence or records a cross-team design decision.

## Future acceptance criteria and tests

- Same accepted payload and nonce produce identical SHA-256 bytes on both peers.
- Commit traffic does not reveal payload or nonce early.
- Correct reveal verifies; changed payload, nonce, identity, or step fails.
- Duplicate, missing, out-of-order, and illegal state transitions are rejected.
- A mismatch produces technical loss `0` without continuing the game.
- Normal and failure paths are reachable only through the SDK.

No cryptographic implementation is included in M1.
