# Option B Interoperability Decision

Decision date: 2026-07-28

Status: **RECORDED PROJECT DECISION — M1 PROFILE IN PROGRESS**

## Decision

The project selects **Option B** for future cross-peer interoperability, pinned to
upstream reference commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54`.

This document records the decision only. It does not copy or freeze any peer-owned
schema or shared-contract byte, and it does not implement live runtime behavior. The
conformance checker remains fail-closed at `PENDING` until an exact accepted profile
revision is recorded.

## Future public endpoints

The future FastMCP surface will expose:

- `negotiate`
- `receive_move` — the book's named turn tool (§2.3.2), superseding the earlier
  Option-B `receive_move` name per the 2026-07-28 coordinator ruling
- `receive_reveal` — the required book Step-3 live reveal
- `submit_audit`
- `receive_control` (optional)

`submit_audit` is the **server** tool. `exchange_audit` is only a **client-side**
method and is never exposed as a server tool.

## Commit-reveal shape — SUPERSEDED BY BOOK on 2026-07-28

> The Option-B commit-reveal construction and no-live-reveal flow below were **reversed**
> by the coordinator on 2026-07-28 in favour of the book construction and the book's
> four-step flow. See
> [COORDINATOR_RULING_COMMIT_REVEAL_2026-07-28.md](COORDINATOR_RULING_COMMIT_REVEAL_2026-07-28.md)
> and `ADR-0006`.

Book-ruled construction now in force:

- The nonce is a field **inside** the hashed JSON payload; there is **no delimiter**.
- Serialization is the book's `json.dumps(sort_keys=True, separators=(",", ":"))` with
  default `ensure_ascii=True` (non-ASCII escaped), UTF-8 encoded, then SHA-256.
- The turn flow is the book's four steps: Commit → Acknowledge → live Reveal
  (Move + Hint, nonce hidden) → Final Reveal (all nonces at end of game).

Superseded Option-B shape (retained for history, not implemented): true `move`,
`position`, `intent`, and `nonce` revealed only in the final audit, with the commitment
computed over canonical JSON, a literal `"|"` separator, and an external nonce.

The exact committed field set and names remain an `UNKNOWN` (`U-005`); this ruling fixes
the construction and flow, not the full field roster.

## Authorization boundary

| Item | Status |
|---|---|
| Contract-independent M2 domain implementation | **GO** (this branch) |
| Option B decision documentation | **GO** (this file) |
| Thief-authored M1 conformance profile and neutral-stub evidence | **IN PROGRESS** |
| FastMCP / commit-reveal / live peer runtime | **PENDING** in later milestones |
| Copying any peer bundle | **SUPERSEDED** under `THIEF-002` |

M2 domain work below is deliberately contract-independent: it uses only Appendix E/F
`CONFIRMED` rules and takes all board, barrier, and position inputs explicitly. It does
not depend on any shared-contract byte, MCP endpoint, or Cop-owned file.

See [COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md) for the
contract gate state and [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md) for the
verified domain parameters.
