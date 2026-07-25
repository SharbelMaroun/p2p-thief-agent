# Repository Audit

Audit updated: 2026-07-24.

## Remediation summary

| Area | Current state | Status |
|---|---|---|
| Active runtime configuration | None | `CONFIRMED` |
| Thief configuration drafts | `config/drafts/thief/` with `.unverified` names | `CONFIRMED` |
| Cop configuration drafts | `archive/pre-audit/opposite-role-config/cop/` | `CONFIRMED` |
| `_audit_status` fields | Absent from all JSON files | `CONFIRMED` |
| README | Corrected for verified-requirements phase and canonical links | `CONFIRMED` |
| Shared structural baseline | `SR-001`–`SR-006` and `PS-001`–`PS-009` confirmed | `CONFIRMED` |
| Appendix F values, statuses, filenames, provider modes, and official addresses | Directly verified from the original PDF | `CONFIRMED` |
| Supplied JSON artifact structures and key sets | Directly inspected from four templates | `CONFIRMED` |
| Formal JSON Schema validation rules, exact MCP messages/tools, and unverified simulator details | Not resolved | `UNKNOWN` |
| Implementation/package/test files | Not added by this remediation | `CONFIRMED` |

## Current-file classification

| Path/group | Current purpose | Classification | Required action |
|---|---|---|---|
| `README.md` | Verified-requirements entry point | KEEP | Maintain only ledger-backed claims |
| `LICENSE` | Repository license | KEEP WITH WARNING | Apply only to team-authored material where legally valid; review final licensing |
| `.env-example` and `.gitignore` | Secret-handling scaffolding | KEEP | `.env-example` exists with placeholders only; keep secrets ignored |
| `.vscode/settings.json` | Editor-local settings | REMOVE LATER | Do not treat as course configuration |
| `config/README.md` | Configuration quarantine policy | KEEP | Update only after official config evidence |
| `config/drafts/thief/*` | Preserved Thief drafts | QUARANTINE | Never load; replace only from verified sources |
| `archive/pre-audit/opposite-role-config/*` | Preserved Cop/opposite-role material | KEEP WITH WARNING | Never use in Thief implementation |
| `docs/REQUIREMENTS_LEDGER.md` | Full confirmed/role ledger | KEEP | Synchronize shared IDs with Cop |
| `docs/SHARED_REQUIREMENT_BASELINE.md` | Shared confirmed baseline | KEEP | Keep free of gameplay/simulator details |
| `docs/UNKNOWN_REQUIREMENTS.md` | Blocking unknowns | KEEP | Resolve only with direct evidence |
| `docs/SPECIFICATION_CONFLICTS.md` | Conflicts/discrepancies | KEEP | Do not silently select a side |
| `docs/VERIFICATION_POLICY.md` and `docs/SOURCE_OF_TRUTH.md` | Evidence controls | KEEP | Apply before implementation |
| `docs/PLAN.md`, `docs/PRD*.md`, `docs/TODO.md` | Verified-phase planning stubs | KEEP | Expand only from confirmed ledger entries |
| `docs/PROMPT_LOG.md` | Canonical prompt-engineering log | KEEP WITH WARNING | Provenance is not requirement evidence |
| `docs/SIMULATOR_BASELINE.md` | Earlier local inspection record | KEEP WITH WARNING | Await centralized verified export |
| `Material/*` | Local references/navigation aids | KEEP WITH WARNING / QUARANTINE | Do not stage or treat translations/summaries as binding |

No teammate material was permanently deleted. Historical opposite-role configuration is
archived, and superseded design drafts are preserved under `archive/pre-audit/`.

Documentation completeness for this evidence-review phase does not mean submission
completeness. Implementation, tests, formal schema validators, match evidence, repository
access, release tagging, and current Moodle instructions remain separate submission
gates.
