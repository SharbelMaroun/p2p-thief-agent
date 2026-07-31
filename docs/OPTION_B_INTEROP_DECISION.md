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

## Future public endpoints — SUPERSEDED 2026-07-29

> **Do not build from this list.** It records the 2026-07-28 book-aligned surface,
> which the simulator-wire adoption replaced the next day. The live tool surface is
> **`negotiate`, `receive_turn`, `submit_audit`, optional `receive_control`** — four
> tools, no `receive_move`, no separate live-reveal tool — specified in
> [SIM_WIRE_PROTOCOL.md](SIM_WIRE_PROTOCOL.md) and mirrored in
> [PRD_p2p_mcp.md](PRD_p2p_mcp.md).

The superseded 2026-07-28 surface was:

- `negotiate`
- `receive_move` — the book's named turn tool (§2.3.2), adopted over the earlier
  Option-B `receive_turn` name per the 2026-07-28 coordinator ruling
- `receive_reveal` — the book Step-3 live reveal
- `submit_audit`
- `receive_control` (optional)

That ruling was itself reversed on 2026-07-29, restoring `receive_turn` and dropping
the separate live-reveal tool: the reveal travels in the audit payload.

`submit_audit` is the **server** tool. `exchange_audit` is only a **client-side**
method and is never exposed as a server tool. That part still holds.

## Commit-reveal shape — reversed twice; read the last block only

> **1. Option-B (original, below): superseded 2026-07-28.** The coordinator reversed it
> in favour of the book construction. That ruling is archived at
> `archive/pre-sim-realign/COORDINATOR_RULING_COMMIT_REVEAL_2026-07-28.md` together with
> the now-superseded `ADR-0006`.
>
> **2. Book construction: superseded 2026-07-29.** Commit `11d0c7a` replaced the whole
> protocol layer with the simulator-conformant wire, which restores the external nonce
> and the `"|"` delimiter. The book-ruled bullets that used to stand here were removed
> because they describe neither the shipped code nor any live decision.
>
> **3. In force today** — see [SIM_WIRE_PROTOCOL.md](SIM_WIRE_PROTOCOL.md) (`ACTIVE`):
>
> ```text
> commit = SHA256(canonical_json(payload) + "|" + nonce)   # nonce OUTSIDE the payload
> canonical_json = json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":"))
> ```
>
> The Option-B text preserved below therefore happens to match the shipped construction
> again, but it is retained as history: the authority for the current wire is
> `SIM_WIRE_PROTOCOL.md`, not this document.

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
