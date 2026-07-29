# Archived — pre-simulator-realignment Option-B protocol

These artifacts are **superseded and retained for history only.** Do not build on them.

On 2026-07-29 the coordinator relayed the lecturer's authoritative ruling that the
reference simulator `Game-P2P-Cop-Chase` (rmisegal) **defines the wire serialization**;
the project book governs concepts and rules. The Thief protocol layer was re-aligned to
the simulator wire (envelope-free `TurnMessage`/`ControlMessage`/`AuditPayload`,
`SHA256(canonical_json(payload) + "|" + nonce)` commitments with
`ensure_ascii=False`, a single `canonical_sha256` for config/audit, `negotiate` /
`receive_turn` / `submit_audit` / `receive_control` tools, and result claims
`capture`/`survival`/`timeout`). See `docs/SIM_WIRE_PROTOCOL.md`.

The self-authored **Option-B** conformance profile that previously lived here proved
its own profile against a neutral stub — but that profile did not match the simulator,
so it could not interoperate with a simulator-conformant classmate opponent.

## Contents

- `WIRE_CONFORMANCE_PROFILE.md` — the superseded Option-B wire profile.
- `0006-commit-reveal-canonicalization.md` — ADR for the withdrawn book-literal commit
  construction (nonce inside the payload, no delimiter, `ensure_ascii=True`).
- `COORDINATOR_RULING_COMMIT_REVEAL_2026-07-28.md` — the 2026-07-28 ruling that adopted
  the book-literal construction, itself superseded by the 2026-07-29 simulator ruling.
- `neutral_stub/` — the independent Node stub that mirrored the Option-B wire.

The corresponding Option-B Python modules and tests were removed from the active tree;
they remain in git history before this commit.
