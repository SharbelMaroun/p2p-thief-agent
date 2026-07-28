# Option B Interoperability Decision

Decision date: 2026-07-28

Status: **RECORDED PROJECT DECISION — RUNTIME DEFERRED**

## Decision

The project selects **Option B** for future cross-peer interoperability, pinned to
upstream reference commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54`.

This document records the decision only. It does not author, copy, or freeze any
parity-controlled schema or shared-contract byte, and it does not implement runtime
behavior. The shared-contract checker remains fail-closed at `PENDING` until a new
coordinator-authorized handoff arrives.

## Future public endpoints

The future FastMCP surface will expose:

- `negotiate`
- `receive_turn`
- `submit_audit`
- `receive_control` (optional)

`submit_audit` is the **server** tool. `exchange_audit` is only a **client-side**
method and is never exposed as a server tool.

## Commit-reveal shape (recorded, not implemented)

- True `move`, `position`, `intent`, and `nonce` are revealed only in the final audit.
- The commitment is computed over canonical JSON, a literal `"|"` separator, and the
  nonce.

The complete canonicalization profile (Unicode escaping, number rendering,
cross-language vectors) is still governed by `U-002`/`ADR-0006` and the coordinator's
2026-07-28 verdict; this decision fixes only the composition shape, not the full
byte-level specification.

## Authorization boundary

| Item | Status |
|---|---|
| Contract-independent M2 domain implementation | **GO** (this branch) |
| Option B decision documentation | **GO** (this file) |
| Copying the old Cop `0.1.0-proposed` bundle | **NO** |
| FastMCP / commit-reveal / shared-contract runtime | **WAIT** for Cop `0.2.0-proposed` |

M2 domain work below is deliberately contract-independent: it uses only Appendix E/F
`CONFIRMED` rules and takes all board, barrier, and position inputs explicitly. It does
not depend on any shared-contract byte, MCP endpoint, or Cop-owned file.

See [COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md) for the
contract gate state and [PARAMETERS_BASELINE.md](PARAMETERS_BASELINE.md) for the
verified domain parameters.
