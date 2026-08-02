# Unknown Requirements

An unknown affects only its named dependent scope. It keeps that choice `PENDING`; it
does not stop unrelated work.

| ID | Still-open question | Dependent scope | Evidence/decision needed |
|---|---|---|---|
| U-002 | ~~Exact canonical serialization, `config_sha256` scope, and byte-comparison procedure~~ | ~~Crypto/config/reporting~~ | **SETTLED 2026-07-29** by adopting the simulator wire: one `canonical_sha256` (`sort_keys`, `ensure_ascii=False`, compact separators) across commitment, config, and audits. Unilateral adoption, not cross-peer agreement — see the re-alignment note below and `SIM_WIRE_PROTOCOL.md` |
| U-003 | ~~Exact MCP tool names, message fields, envelopes, sizes, acknowledgements, idempotency~~ | ~~Networking~~ | **SETTLED 2026-07-29**: `negotiate` / `receive_turn` / `submit_audit` / `receive_control`, no envelope. Not yet exercised against a live opponent |
| U-004 | ~~Exact handshake wire sequence and transition ordering~~ | ~~Handshake~~ | **SETTLED 2026-07-29** by `protocol/handshake.py` (signed terms, role-free identity). The separate **Step-0 hardware attestation** of rule 24 is unimplemented and tracked in `TODO.md`, not here |
| U-005 | ~~Exact committed payload construction and nonce encoding/length~~ | ~~Cryptography~~ | **SETTLED 2026-07-29**: `SHA256(canonical_json(payload) + "\|" + nonce)`, nonce outside the payload, `token_hex(16)`. Verification re-hashes the payload as received, so no cross-peer field roster is required |
| U-006 | Exact peer ports and local endpoint configuration | Networking | Accepted private-config design; official values if any |
| U-009 | Gmail draft-versus-send mode and exact OAuth/credential workflow | Reporting | Appendix A, dated clarification, or accepted ADR-0010 |
| U-010 | Whether a shared executable stateless package is permitted | Packaging | Lecturer clarification; this repository consumes no peer package |
| U-013 | Complete private TOML keys, types, secret-loading method, and compatibility rules | Configuration | ADR-0004; `config/game.toml`, its private role, major categories, and JSON precedence are confirmed in `AB-001`; the full schema and secret-loading method remain open |
| U-014 | Non-quantitative event ordering: moves/barriers/capture, scent emission/decay/observation, and scoring edge cases | Domain/protocol | Direct book sections plus accepted shared rules |
| U-015 | Scope permitted for simulator code reuse under its license/provenance | Provenance | License/lecturer review and ADR-0008 |
| U-017 | Newer Moodle instructions and lecturer announcements | Potential final-release areas | Obtain dated official posts |
| U-019 | Official template required/optional fields, types, enums, bounds, and additional-property rules | Artifact validation | Formal schemas or dated authoritative clarification |
| U-021 | ~~Exact six-sub-game role assignment~~ | ~~League scheduling~~ | **CLOSED 2026-07-29.** Reopened 2026-07-28 by coordinator verdict, then closed the following day when the required lecturer answer was obtained and relayed by the coordinator: sub-games 1, 3, 5 natural role, 2, 4, 6 swapped, **Thief moves first**. Provenance is a coordinator-relayed lecturer answer, not a Moodle announcement, and is recorded at that level. See the closure note below and `C-012`. |
| U-022 | ~~Whether surviving *exactly* `[Survival Threshold]` turns is a Thief win~~ | ~~Terminal-outcome scoring; series aggregation~~ | **CLOSED 2026-07-31.** The book resolves it without a coordinator ruling. Chapter 3 table 2 (PDF p. 38) defines the survival row as the Thief surviving "the limit of valid moves" without capture, and Appendix F table 15 sets `[Step Limit]` and `[Survival Threshold]` to the same value, so the horizon test is **inclusive**: completing the final step uncaptured is a Thief win. `resolve_outcome` already used `steps >= survival_threshold`; the reading is now recorded and covered by a boundary test. See `C-017` |
| U-023 | ~~Whether the shared match object must carry `pheromone_min_center_intensity`~~ | ~~Pre-play agreement; cross-peer interoperability~~ | **CLOSED 2026-08-01, and it found a real bug here.** Checked against the **book PDF itself** and the lecturer's artifact templates. Appendix F table 16 has exactly **three** rows, all `Fixed` — centre intensity `0.9`, decay `0.10`, field `5x5` — and **no** minimum or floor row; the lecturer's own `agreed-config` template carries the same three keys and no fourth. This repository had `min_center_intensity` in `REQUIRED_TERMS`, so it would have refused **the very template teams are meant to share**, reporting it as a missing agreed term. Removed from `REQUIRED_TERMS` and kept in `AGREEMENT_TERMS` so it is still compared when a peer sends it; a regression test pins that the three-key shape is accepted. The pinned simulator does require the key, but a simulator behaviour contradicting both the book and the lecturer's template is not authority `[SOURCE_OF_TRUTH]`. The companion peer needed no change — its optional reading was right |

| U-025 | Emission value of the eight `5×5` cells at squared-distance 5 (the `(±1,±2)`/`(±2,±1)` ring) | Scent emission (`M6-001`), and any belief update that reads the raw field | Book Figure 4 (p.44) names only five distance classes — centre `0.90`, cross `0.62`, diagonal `0.20`, mid-side `0.14`, corner `0.04` — covering 17 of 25 cells. The remaining eight are unnamed. `perception/scent._PROVISIONAL_D2_5` holds a documented residual (`0.04`, matching "edges absorb only a residual amount", p.43) pending a coordinator ruling or a dated lecturer answer; it is flagged in code and pinned by a test, never silently chosen. Opened 2026-08-02 |

## Authoritative lecturer answers — 2026-07-29

The coordinator relayed the lecturer's authoritative interop answers. As recorded, that
relay contains **two clauses that conflict for commit-reveal**: that "the book
construction is retained where it conflicts with the simulator", and that the reference
simulator `Game-P2P-Cop-Chase` (rmisegal — a sanctioned learning aid, distinct from the
`THIEF-002`-forbidden companion Cop repo) "defines exact wire serialization" while the
book "remains authoritative for concepts and rules".

**Which clause governs, and why.** Commit-reveal byte layout *is* wire serialization, so
the second clause is the specific one and it controls; the first is the general
concepts-and-rules statement. This repository therefore follows the simulator for the
hash construction and the book for game rules and scoring. Verified 2026-07-31 against
the simulator source itself (`src/police_thief/domain/crypto.py`, read via the lecturer's
`Game-P2P-Cop-Chase` NotebookLM): it serializes with
`json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))` and
concatenates the nonce **outside** the payload behind a `|` separator — byte-for-byte
what `protocol/crypto.py` implements.

This is a deliberate, disclosed reading of an ambiguous instruction, not a silent
simulator default. It is disclosed under the book p. 5 contradiction clause. If the
coordinator obtains an unambiguous lecturer answer preferring the book construction, the
wire must be re-aligned and this section reversed — interoperability with classmates,
who will build from the same simulator, is the reason for the current choice.

Resolved on this basis:

- **U-021 role scheduling — CLOSED.** Six-sub-game series alternates roles: sub-games
  1, 3, 5 use the natural role and 2, 4, 6 the swapped role; the **Thief always moves
  first** every sub-game. `LS-001` promoted to CONFIRMED per this lecturer answer relayed
  and accepted by the coordinator on 2026-07-29. Dependent scope: M7 series orchestration.
- **U-014 event ordering — CLOSED.** Within a turn: apply the move, emit scent at the new
  cell, apply grid-wide decay `τ(t+1)=max(0,(1-ρ)τ+Δτ)`, then evaluate capture/victory
  after position and barrier updates. Dependent scope: M6 scent and the turn state machine.
- **U-005 committed payload / nonce — superseded 2026-07-29.** This entry recorded a
  2026-07-28 "keep book" ruling (nonce inside the sorted-compact payload, no delimiter,
  `ensure_ascii=True`) and stated that the simulator variant was "not adopted". **The
  wire re-alignment described below then happened**, and the simulator variant *was*
  adopted. The paragraph is retained only to date the reversal.

**The re-alignment is done, not pending.** Commit `11d0c7a` ("replace Option-B profile
with simulator wire; archive old layer") replaced the Option-B protocol layer on
2026-07-29. The shipped surface is now the simulator's: tools `negotiate` /
`receive_turn` / `submit_audit` / `receive_control`, one canonical-JSON
`config_sha256`, role-free negotiation identity, `result_claim ∈ {capture, survival,
timeout}`, and

```text
commit = SHA256(canonical_json(payload) + "|" + nonce)
canonical_json = json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":"))
```

The authoritative record is [SIM_WIRE_PROTOCOL.md](SIM_WIRE_PROTOCOL.md) (status
`ACTIVE`). `U-002`, `U-003`, `U-004`, and `U-005` are settled **by that adoption**, not
by a fresh lecturer answer. The Option-B modules the earlier text referenced
(`protocol/canonical.py`, `protocol/commitment.py`, `protocol/negotiation.py`) were
deleted in the same commit; the archived profile and its coordinator ruling are kept at
`archive/pre-sim-realign/`. See the ADR-0006 note in [adr/README.md](adr/README.md).

## Provisional implementations as of 2026-07-29 (still OPEN)

The code now embodies a working, provisional choice for several of the items above. These
notes record *what the implementation currently assumes* so it is auditable; they do
**not** close the UNKNOWN. Under the standing rule that provisional shared-contract
foundations must not be finalized, closure remains an explicit coordinator verdict. The
coordinator delegated the handling of these on 2026-07-29 and this conservative
"note-but-keep-open" recording was chosen deliberately.

This table described the **pre-realign** Option-B layer and named modules that no longer
exist. It is replaced by the shipped state below.

| ID | Implementation in the shipped code | Status |
|---|---|---|
| U-002 | Single canonical JSON in `protocol/crypto.py` (`sort_keys=True`, `ensure_ascii=False`, compact separators); one `canonical_sha256` serves the commitment, the agreed config, and audits | Settled by the 2026-07-29 wire adoption; no cross-peer acceptance yet |
| U-003 | Tools `negotiate` / `receive_turn` / `submit_audit` / `receive_control` with no envelope — the tool argument *is* the message dict (`protocol/wire.py`) | Settled by the 2026-07-29 wire adoption; not exercised against a live opponent |
| U-004 | Signed-terms handshake in `protocol/handshake.py`: each peer signs `commit_of(terms, nonce)` and verifies the opponent signed the same terms; identity carries no role | Settled by the 2026-07-29 wire adoption; Step-0 hardware attestation is still unimplemented |
| U-005 | `commit = SHA256(canonical_json(payload) + "\|" + nonce)`, nonce **outside** the payload, `secrets.token_hex(16)`; sealed step roster in `protocol/sealing.py` | Settled by the 2026-07-29 wire adoption; verification re-hashes the payload as received, so the opponent's field roster is never constrained |
| U-014 | Capture precedence and terminal technical-loss scoring in `domain/capture.py` and `state/scoring.py` | **OPEN** — full live-turn event ordering still unresolved |

The settled rows describe a unilateral adoption of the simulator wire, not a bilateral
agreement. None of them binds an unknown opponent until a live interoperability run
proves it.

## Closed in this reconciliation

README component count and tag naming are confirmed in `SR-007`/`SR-008`. Appendix F
values, rate limits/timeouts, provider modes, both official addresses, and filename
patterns are confirmed in `AF-013..022`. Moodle/PDF rules and screenshot evidence are
confirmed in `SR-011..013`. The shared/private configuration boundary, mandatory
`agreed_between` field, common artifact identity, and core commit serialization are
confirmed in `AB-001..002`, `AR-001`, and `CR-001`. JSON template key presence is
confirmed in `JS-001..003`. Final reports are JSON attachments without a free-text
report body (`AE-032`). Exact constraints beyond that evidence remain open above.

`U-016` is closed by the verified identity in [TEAM_INFO.md](TEAM_INFO.md). `U-020` is
`SUPERSEDED` by `THIEF-002`: no peer manifest or parity-file handoff is part of the
current conformance workflow.

**U-021 — briefly closed then REOPENED 2026-07-28:** Role alternation was
provisionally recorded as `CONFIRMED` from course material on 2026-07-28. The same-day
coordinator verdict (`ACCEPTED_FOR_PROVISIONAL_PARITY: NO`) explicitly rejected that
promotion: odd-natural/even-opposite alternation is simulator-confirmed but **not**
book-confirmed, and the recorded course/lecturer direction is not an authenticated
Moodle announcement or original lecturer message. `U-021` is therefore reopened and
`LS-001` is reverted to `UNKNOWN`. Alternation must not be treated as binding in
normative contract documents until an authenticated lecturer answer is obtained. See
[COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md).

**U-021 — CLOSED 2026-07-29.** The required lecturer answer was obtained and relayed by
the coordinator: sub-games 1, 3, 5 natural role, 2, 4, 6 swapped, Thief moves first. See
the "Authoritative lecturer answers" section above; `LS-001` is now CONFIRMED.
