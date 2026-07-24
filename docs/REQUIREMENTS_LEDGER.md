# Requirements Ledger

No project-book requirement is currently `CONFIRMED`; direct authoritative text has
not yet been extracted and checked. Rows prevent lower-priority material from silently
becoming requirements.

| ID | Requirement | Status | Mandatory/Recommended/Illustrative | Authoritative source | Exact location | Applies to | Repository impact | Test impact | Notes |
|---|---|---|---|---|---|---|---|---|---|
| AUD-001 | Maintain a Thief-only boundary and retain the Cop companion link | `CONFIRMED` | Mandatory for this audit | User task | “THIEF-SPECIFIC RULE” and “README HANDLING” | Repository/docs | README and audit docs | Structural check | Task constraint, not claimed as a book rule |
| AUD-002 | No code, dependencies, source deletion, or Phase 1 work in this audit | `CONFIRMED` | Mandatory for this audit | User task | Opening constraints/completion conditions | Entire repo | Documentation only | Diff check | Task-scoped |
| AUD-003 | Use only `CONFIRMED`, `CONFLICT`, or `UNKNOWN` for uncertain items | `CONFIRMED` | Mandatory for this audit | User task | “CORE NO-ASSUMPTION RULE” | Audit docs | Status vocabulary | Doc check | Task-scoped |
| REQ-REPO-001 | Final submission uses separate Cop and Thief repositories | `UNKNOWN` | Unknown | Official book v3.0.0 | Team note claims PDF pp. 95–96; direct check pending | Structure | Preserve separation | Independence test later | Lower source insufficient |
| REQ-RUNTIME-001 | Peers run independently without shared live state | `UNKNOWN` | Unknown | Official book / Appendix E | Direct location pending | Architecture | Blocks runtime design | Isolation tests later | User task separately prohibits Cop dependency here |
| REQ-CONFIG-001 | Signed/shared JSON and private TOML split is required | `UNKNOWN` | Unknown | Official book / templates | Direct location pending | Config | Current configs quarantined | No validation yet | Simulator behavior insufficient |
| REQ-GAME-001 | Binding game values and modes match Appendix F | `UNKNOWN` | Unknown | Appendix F | Exact table pending | Game/config | Blocks gameplay | Blocks game tests | No value admitted |
| REQ-PROTOCOL-001 | Exact messages, MCP tools, acknowledgement, and cryptographic sequence | `UNKNOWN` | Unknown | Official book/templates | Exact sections pending | Network/crypto | Blocks protocol | Blocks contract tests | Simulator is illustrative |
| REQ-THIEF-001 | Official Thief evasion, belief/scent, survival, and truth/bluff behavior | `UNKNOWN` | Unknown | Official book | Exact sections pending | Strategy | Blocks strategy | Blocks strategy tests | Audit task only requires these as doc topics |
| REQ-REPORT-001 | Exact artifact count/names/schemas/signatures/ownership/email flow | `UNKNOWN` | Unknown | Moodle templates/book | Templates/sections pending | Reporting | Blocks reporting | Blocks schema tests | “Four” remains unverified |
| REQ-README-001 | Exact README/report sections and count | `UNKNOWN` | Unknown | Book/guidelines | Exact sections pending | README | Placeholders only | Doc review | Six-section claim quarantined |
| REQ-SUBMIT-001 | Exact tag and submission workflow | `UNKNOWN` | Unknown | Moodle/guidelines | Direct location pending | Release | Do not tag | Release checklist later | Examples insufficient |
| REQ-QUALITY-001 | Exact Python/uv/Ruff/coverage/file/package rules | `UNKNOWN` | Unknown | Original professional guidelines | Original absent | Tooling | No package metadata | Blocks quality setup | Summary is navigation only |
