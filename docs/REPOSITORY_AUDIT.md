# Repository Audit

Audit date: 2026-07-24. “Verified” means verified for present repository purpose, not
that embedded project claims are authoritative.

| Path | Current purpose | Classification | Verified statements | Unsupported statements | Required action | Blocking evidence needed |
|---|---|---|---|---|---|---|
| `.env-example` | Placeholders | REVISE | No literal secret found | Provider/model names and need | Keep inactive; revise later | Official integrations/design |
| `.gitignore` | Ignore local/secrets | KEEP WITH WARNING | Ignores `.env` and common secrets | Exact artifact paths | Keep; re-audit later | Original guidelines |
| `.vscode/settings.json` | Editor settings | REMOVE LATER | Editor-only | Tool assumptions | Do not treat as requirement | Tooling policy |
| `LICENSE` | MIT text | KEEP WITH WARNING | Standard license text | Applicability to future/course material | Keep | Ownership decision |
| `README.md` | Entry point | REVISE | Companion URLs/audit status | Old runtime, section-count, install, config claims | Replaced safely | Official report/package rules |
| `config/README.md` | Configuration quarantine notice | KEEP | Correctly records audit state | None; it does not define schema or values | Keep until configs are verified/replaced | Confirmed config requirements |
| `config/police/game.json` | Cop shared-config draft | REMOVE LATER | Valid JSON | All schema/values; wrong role | Retain only; never consume | Schema/removal approval |
| `config/police/game.toml` | Cop local-config draft | REMOVE LATER | Companion URLs | Ports/timeouts/models/email/modes | Retain only; never consume | Requirements/removal approval |
| `config/police/rate_limits.json` | Cop limit draft | REMOVE LATER | Valid JSON | Version/all limits | Retain only; never consume | Requirements/removal approval |
| `config/thief/game.json` | Thief shared-config draft | QUARANTINE | Valid JSON | Schema/version/all values | Do not overwrite/use | Appendix F/templates |
| `config/thief/game.toml` | Thief private-config draft | QUARANTINE | Companion URLs | Version/ports/timeouts/models/email/fields | Do not use | Official rules/team choices |
| `config/thief/rate_limits.json` | Thief limit draft | QUARANTINE | Valid JSON | Version/quotas/queue/retry | Do not use | Official/provider constraints |
| `docs/PLAN.md` | Architecture plan | QUARANTINE | Useful topic inventory | Modules/messages/schemas/values/dependencies/tests | Banner; rewrite later | Confirmed ledger |
| `docs/PRD.md` | Product draft | QUARANTINE | Candidate inventory | Numeric/protocol/reporting/tooling claims | Banner; rebuild later | Official sources |
| `docs/PRD_commit_reveal.md` | Crypto draft | QUARANTINE | Candidate questions | Payload/hash/sequence/sanctions | Banner; do not implement | Protocol/templates |
| `docs/PRD_gatekeeper_reporting.md` | Reporting draft | QUARANTINE | Candidate area | Artifacts/Gmail/limits/address | Banner; do not implement | Templates/book |
| `docs/PRD_p2p_mcp.md` | Network draft | QUARANTINE | Candidate area | Tools/messages/timeouts/rules | Banner; do not implement | Official protocol |
| `docs/PRD_scent_belief.md` | Perception draft | QUARANTINE | Thief-relevant topic | Dimensions/formulas/schemas | Banner; do not implement | Appendix F/book |
| `docs/PRD_strategy.md` | Strategy draft | KEEP WITH WARNING | Thief evasion/belief focus | Interfaces/weights/exact behaviors | Banner; ideation only | Role rules/team design |
| `docs/PROMPTS.md` | Prompt history | KEEP WITH WARNING | Planning provenance | Outputs are not evidence | Retain only as provenance | Prompt-log requirement |
| `docs/TODO.md` | Work breakdown | QUARANTINE | Candidate inventory | Counts/phases/files/requirements/values | Banner; do not start | Verified ledger/plan |
| `Material/LECTURER_REPO_OVERVIEW.md` | Simulator summary | KEEP WITH WARNING | Intended URL/path | Missing upstream commit; stale test result | Navigation only | Pinned checkout |
| `Material/PROJECT_CONTEXT(1).md` | Planning context | KEEP WITH WARNING | Warns against assumptions | Unverified examples/designs | Navigation only | Official sources |
| `Material/SUBMISSION_CHECKLIST(1).md` | Planning checklist | KEEP WITH WARNING | Useful coverage list | Checkmarks/claims are not evidence | Treat claims unverified | Official sources |
| `Material/software_submission_guidelines-V3_Summary.md` | Summary | KEEP WITH WARNING | Names intended source | All mandates until original checked | Navigation only | Original v3.0 |
| `Material/reference/police_thief_p2p.pdf` | Intended book | KEEP WITH WARNING | File exists | Version/content not directly verified here | Preserve/verify | Provenance/reader |
| `Material/reference/police_thief_p2p_unverified_translation.md` | Translation | QUARANTINE | Explicitly unverified | All translated content | Navigation only | Original PDF |

The ten audit control documents created by this task are classified `KEEP`.
