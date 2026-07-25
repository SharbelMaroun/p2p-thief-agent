# Unknown Requirements

An unknown blocks only its named subsystem.

| ID | Still-open question | Blocks | Evidence/decision needed |
|---|---|---|---|
| U-002 | Exact canonical serialization, signature computation, identity binding, and byte-comparison procedure | Crypto/config/reporting | Binding protocol text or accepted ADR-0006 |
| U-003 | Exact MCP tool names, message fields, envelopes, maximum sizes, acknowledgements, and idempotency rules | Networking | Cop proposal plus accepted ADR-0001/0002 |
| U-004 | Exact Step-0 wire sequence and transition ordering | Handshake | Direct official section and accepted state-machine contract |
| U-005 | Exact committed payload field set and nonce encoding/length | Cryptography | Binding protocol/template evidence or accepted ADR |
| U-006 | Exact peer ports and local endpoint configuration | Networking | Accepted private-config design; official values if any |
| U-009 | Gmail draft-versus-send mode and exact OAuth/credential workflow | Reporting | Appendix A, dated clarification, or accepted ADR-0010 |
| U-010 | Whether a shared executable stateless package is permitted | Packaging | Lecturer clarification; M1 uses independent byte copies only |
| U-013 | Exact private TOML filename, keys, types, and compatibility rules | Configuration | ADR-0004 and source-backed Cop proposal |
| U-014 | Non-quantitative event ordering: moves/barriers/capture, scent emission/decay/observation, and scoring edge cases | Domain/protocol | Direct book sections plus accepted shared rules |
| U-015 | Scope permitted for simulator code reuse under its license/provenance | Provenance | License/lecturer review and ADR-0008 |
| U-016 | Team/group/member identifiers and eight-character team code | Identity/reporting | Verified team input |
| U-017 | Newer Moodle instructions and lecturer announcements | Potential final-release areas | Obtain dated official posts |
| U-019 | Official template required/optional fields, types, enums, bounds, and additional-property rules | Artifact validation | Formal schemas or dated authoritative clarification |
| U-020 | Exact accepted parity-file list, contract version, manifest shape, and hashes | Contract gate | Source-backed Cop proposal and Thief review |

## Closed in this reconciliation

README component count and tag naming are confirmed in `SR-007`/`SR-008`. Appendix F
values, rate limits/timeouts, provider modes, both official addresses, and filename
patterns are confirmed in `AF-013..022`. JSON template key presence is confirmed in
`JS-001..003`. Final reports are JSON attachments without a free-text report body
(`AE-032`). Exact constraints beyond that evidence remain open above.
