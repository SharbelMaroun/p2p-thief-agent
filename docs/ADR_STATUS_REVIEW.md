# ADR Status Review

Review date: 2026-07-28

This is an **inventory only**. It changes no ADR status, accepts nothing, and
authorizes no runtime behavior. `docs/adr/README.md` remains the status index; where
this review and that index disagree about maturity, the index is authoritative until a
status is deliberately changed.

Purpose: `PLAN.md` states that schema versions, participant/match binding,
canonicalization, `config_sha256` scope, extension policy, and neutral-opponent failure
semantics "must be settled before M2". None are settled. M2 proceeded under the
2026-07-28 contract-independent carve-out, which was legitimate, but the ADR debt is
real and this review makes it explicit rather than leaving it implied.

Current tally: **7 `Pending`, 3 `Proposed`, 0 accepted.**

## Headline finding

**No ADR mentions the Option B decision of 2026-07-28**, even though Option B proposes
concrete answers to ADR-0001, ADR-0002, and part of ADR-0006. The ADR set is
systematically stale relative to the project's own recorded decision. That staleness is
a documentation gap, not evidence that the decisions were made — Option B is a project
interoperability choice and does not by itself accept any ADR.

## Category A — decidable inside this repository

These need no cross-team agreement. They are blocked only by someone choosing to
decide them.

| ADR | Topic | Why it is local | What it still needs |
|---|---|---|---|
| ADR-0008 | Simulator reuse and licence | Purely a provenance and licensing determination about this repository's own contents | Record the licence at pinned commit `960499fd…4677b54`, plus ownership, permitted reuse, and the clean-room boundary. The conservative position is already in force in practice — `README.md` states no lecturer simulator runtime code is included — so the decision is largely to write down what is already being done. Closing this also unblocks `U-015` and removes the dependency ADR-0005 declares on it. |
| ADR-0007 | LLM movement policy | `AE-025` is a recommendation, not a prohibition, and the choice of a deterministic movement default is a local policy | The confirmed part is already implemented. Note the live inconsistency: `PRD_strategy.md` calls ADR-0007 "the project policy" while its status is only `Proposed`. Either the ADR moves or the PRD wording softens. |
| ADR-0009 | GUI truth model | The binding constraint (local truth only) is confirmed by `AE-008` and `SR-004`; views, fields, and layout are team design choices | Could be accepted for the constraint while leaving layout open. No urgency: GUI is M8. |
| ADR-0010 | Gmail reporting | Address roles (`AF-020`) and JSON-attachment-only with no free-text body (`AE-032`) are confirmed | Could be accepted for the confirmed part, leaving draft/send mode, MIME details, retries, and idempotency open under `U-009`. No urgency: reporting is M7. |

## Category B — genuinely external

These cannot be closed here at any effort. Each needs an authoritative source or a
cross-team verdict.

| ADR | Topic | Blocking dependency |
|---|---|---|
| ADR-0001 | MCP contract | `U-003`. Option B proposes `negotiate` / `receive_move` / `submit_audit` / optional `receive_control`, but coordinator blocker 6 — interoperability unproven from the book — is open, and the Thief has explicitly referred that tension back to the coordinator. |
| ADR-0002 | Message envelope and idempotency | `U-003`. Option B's `PROTOCOL_PROFILE.md` goes further and *forbids* `protocol_version`, `message_id`, `idempotency_key`, and `sequence`, which is a stronger claim than this ADR contemplates and is itself unaccepted. |
| ADR-0003 | Schema-version discrepancy | Needs authoritative clarification. Unchanged in substance: the Cop `0.2.0-proposed` schema still pins `const: "1.2"` while its own description admits compatibility with 1.1 and 1.3 is unresolved. |
| ADR-0006 | Commit-reveal canonicalization | `U-002`, and identical to coordinator blocker 5. More evidence exists than when drafted — the `0.2.0-proposed` vectors reproduce exactly — but the review found no escaping vector, single-language reproduction only, and a `signature` field that is required with no algorithm defined anywhere. |

## Category C — stale text, unchanged status

Evidence gathered since drafting has moved these on, but the ADR files do not say so.
Refreshing the text would not change any status.

| ADR | What changed after it was written |
|---|---|
| ADR-0004 | `LS-002` confirmed `opponent_url` as a private TOML key on 2026-07-28, and the coordinator's blocker 3 reversed the `rate_limits.json` classification back toward shared. The ADR reflects neither. |
| ADR-0005 | A live contradiction now exists: the Cop `SHARED_RULES.md` asserts the multiplicative scent formula with "Book Ch.4" authority, while Thief ledger `AF-016` records the three constants as `CONFIRMED` but the formula itself as unknown. Recorded as finding N-4 in `CONTRACT_REVIEW.md`. Must be reconciled before either peer implements M6. |
| ADR-0001, ADR-0002 | Both predate the Option B decision and do not reference it, so a reader cannot tell from the ADR alone that a candidate answer exists. |

## Suggested order, if these are taken up

1. **ADR-0008** — fully local, unblocks `U-015`, removes ADR-0005's declared dependency,
   and mostly documents an existing practice.
2. **ADR-0007** — resolve the `PRD_strategy.md` wording contradiction one way or the
   other, now that a deterministic baseline actually exists.
3. **Category C text refresh** — cheap, and stops the ADR set misleading a reader.
4. **ADR-0009 / ADR-0010** — accept the confirmed parts whenever M7/M8 approach.
5. **Category B** — nothing to do but ask the coordinator.

Nothing above may be treated as authorization. An ADR changes status only by a
deliberate decision recorded in `docs/adr/`, and a shared-impact ADR additionally
requires acceptance by both peers under `SOURCE_OF_TRUTH.md`.
