# Unknown Requirements

An unknown affects only its named dependent scope. It keeps that choice `PENDING`; it
does not stop unrelated work.

| ID | Still-open question | Dependent scope | Evidence/decision needed |
|---|---|---|---|
| U-002 | Exact canonical serialization beyond the core commit example, signature computation, identity binding, `config_sha256` scope, and byte-comparison procedure | Crypto/config/reporting | Binding protocol text or accepted ADR-0006; `CR-001` settles only sorted compact UTF-8 for the shown commit payload |
| U-003 | Exact MCP tool names, message fields, envelopes, maximum sizes, acknowledgements, and idempotency rules | Networking | Thief conformance profile plus explicit acceptance of ADR-0001/0002 |
| U-004 | Exact Step-0 wire sequence and transition ordering | Handshake | Direct official section and accepted state-machine contract |
| U-005 | Exact committed payload field set and nonce encoding/length | Cryptography | Binding protocol/template evidence or accepted ADR |
| U-006 | Exact peer ports and local endpoint configuration | Networking | Accepted private-config design; official values if any |
| U-009 | Gmail draft-versus-send mode and exact OAuth/credential workflow | Reporting | Appendix A, dated clarification, or accepted ADR-0010 |
| U-010 | Whether a shared executable stateless package is permitted | Packaging | Lecturer clarification; this repository consumes no peer package |
| U-013 | Complete private TOML keys, types, secret-loading method, and compatibility rules | Configuration | ADR-0004; `config/game.toml`, its private role, major categories, and JSON precedence are confirmed in `AB-001`; the full schema and secret-loading method remain open |
| U-014 | Non-quantitative event ordering: moves/barriers/capture, scent emission/decay/observation, and scoring edge cases | Domain/protocol | Direct book sections plus accepted shared rules |
| U-015 | Scope permitted for simulator code reuse under its license/provenance | Provenance | License/lecturer review and ADR-0008 |
| U-017 | Newer Moodle instructions and lecturer announcements | Potential final-release areas | Obtain dated official posts |
| U-019 | Official template required/optional fields, types, enums, bounds, and additional-property rules | Artifact validation | Formal schemas or dated authoritative clarification |
| U-021 | Exact six-sub-game role assignment, including whether Cop and Thief must alternate every sub-game and which team starts in which role | League scheduling | **REOPENED 2026-07-28 by coordinator verdict.** Simulator confirms odd-natural/even-opposite alternation, but the book does not, and the recorded course/lecturer direction is not an authenticated Moodle announcement. Needs an authenticated lecturer answer before alternation may be treated as binding. See [COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md). |

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
