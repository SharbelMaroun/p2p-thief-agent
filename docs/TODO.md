# Active Task Ledger

Statuses: `DONE`, `IN PROGRESS`, `PENDING`, or `BLOCKED`. `BLOCKED` names a specific
external gate; it does not stop unrelated work.

| ID | Task | Owner | Status | Priority | Requirement / ADR | Test or artifact | Definition of Done |
|---|---|---|---|---|---|---|---|
| M0-001 | Verify baseline, remote divergence, and every Sharbel file change | Thief agent | DONE | P0 | Verification policy | `REPOSITORY_AUDIT.md` | Commit IDs, 3/7 divergence, 21-file triple-dot inventory, and five conflicts are recorded |
| M0-002 | Preserve Appendix E/F and JSON-template evidence | Thief agent | DONE | P0 | `AE-025`, `AF-013..022`, `JS-001..003` | Ledger and schema document | Direct evidence survives reconciliation without weaker derived claims |
| M0-003 | Reconcile the five content conflicts manually | Thief agent | DONE | P0 | Audit table | Documentation review | Each conflict has a chosen side and source-backed rationale |
| M0-004 | Add verified completeness, parameters, GUI, replay, and submission docs | Thief agent | DONE | P1 | `PS-001`, `AE-008`, `AE-020` | Five documents | Documents exist, cite controlling evidence, and make no parity claim |
| M0-005 | Resolve stale README/tag/email unknowns and team-info drift | Thief agent | DONE | P0 | `SR-007`, `SR-008`, `AF-020` | Unknown/conflict registers | Verified facts are removed from unknowns; identity fields remain unknown |
| M1-001 | Add the independently installable uv package scaffold | Thief agent | DONE | P0 | `PS-002`, `THIEF-001` | `pyproject.toml`, `uv.lock`, `src/` | Frozen sync and import succeed; version is defined once at `1.00` |
| M1-002 | Add a public SDK test before its minimal implementation | Thief agent | DONE | P0 | `PS-004`, `PS-007` | `tests/unit/test_sdk.py` | Red test is observed, minimal SDK passes, and no business behavior is added |
| M1-003 | Add CLI/help or import smoke coverage | Thief agent | DONE | P1 | `M1-PRD-003` | `tests/integration/test_cli.py` | Installed entry point returns help and does not start a peer |
| M1-004 | Add Ruff, branch coverage, size, secret, and hash gates | Thief agent | DONE | P0 | `PS-003..006` | `pyproject.toml`, `scripts/` | Local gates execute; hash gate fails closed until the Cop proposal exists |
| M1-005 | Keep environment and private configuration provider-neutral | Thief agent | DONE | P0 | `PS-006`, ADR-0004 | `.env-example`, `.gitignore` | Only dummy optional examples remain and private local files are ignored |
| CT-001 | Inspect Cop proposal commit and its citations | Cop + Thief agents | BLOCKED | P0 | ADR-0001..0006 | Proposal commit | Cop publishes an accessible, source-backed proposal |
| CT-002 | Review fields; copy accepted parity files byte-for-byte | Thief agent | BLOCKED | P0 | Contract policy | Shared bundle | No unsupported field remains and no independent Thief contract is created |
| CT-003 | Verify shared hashes in both repositories | Thief agent | BLOCKED | P0 | Contract manifest | `scripts/check_shared_contracts.py` | Replace the fail-closed pending gate only after every accepted manifest entry matches both repositories |
| EXT-001 | Obtain dated current Moodle instructions | Team | PENDING | P1 | `U-017` | Source inventory | Dated authoritative instructions are archived or absence is documented |
| EXT-002 | Obtain verified simulator export at commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54` | Team | PENDING | P1 | ADR-0008, `U-015` | Provenance record | Exact files/tests and license boundary are reviewed without copying substantial code |

## Next Thief tasks after the contract gate

| ID | Task | Owner | Status | Priority | Requirement / ADR | Planned tests/artifact | Definition of Done |
|---|---|---|---|---|---|---|---|
| M2-001 | Define immutable coordinates, actions, and grid | Thief agent | PENDING | P0 | `AF-013`, `AF-015` | Unit tests | Immutable values reject invalid construction and preserve configured bounds |
| M2-002 | Implement legal movement | Thief agent | PENDING | P0 | `AF-015` | Normal/boundary/illegal unit tests | N/S/E/W/STAY work; diagonals, off-grid moves, and blocked moves fail deterministically |
| M2-003 | Model Thief-local state and history | Thief agent | PENDING | P0 | `SR-004`, `THIEF-001` | Unit tests | State contains only local truth and immutable history snapshots |
| M2-004 | Track known disclosed barriers | Thief agent | PENDING | P0 | `AE-015` | Unit tests | Disclosed barriers affect legal moves without exposing Cop-private state |
| M2-005 | Implement barrier-on-current-cell capture | Thief agent | PENDING | P0 | `AE-046` | Capture unit test | A disclosed barrier placed on the current Thief cell produces capture |
| M2-006 | Implement trapped-Thief capture | Thief agent | PENDING | P0 | `AE-046` | Capture unit tests | No legal action other than blocked stay/escape produces trapped capture per accepted ordering |
| M3-001 | Add deterministic baseline survival policy | Thief agent | PENDING | P1 | `AE-025`, ADR-0007 | Strategy unit tests | Policy selects only legal actions deterministically and contains no LLM call |

The archived 635-task document remains historical coverage under
`archive/pre-audit/documentation/TODO.md`; it is not the active plan.
