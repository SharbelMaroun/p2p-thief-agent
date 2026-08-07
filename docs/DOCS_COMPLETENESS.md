# Documentation Completeness

Presence and content maturity are separate. Every document in `docs/` is listed below
with its current maturity.

**This table is checked, not maintained by hand.**
`scripts/check_ledger_consistency.py` (`G-010`) fails if a document exists without a row,
or a row claims a file that is not in the tree. It found **29 missing rows** on
2026-08-07: the table was last reviewed 2026-07-28, when the repository was still an M1
scaffold, and every row still in it was individually accurate — which is why the gap
survived. That is the argument for the check rather than for another careful pass.

Gate-scoped verification records (`M1_VERIFICATION.md`, `M2_DOMAIN.md`,
`M3_LOCAL_STATE.md`), the coordinator verdict, the Stage-C acceptance and the gate
resolution review are deliberately excluded: they record a moment rather than a current
state, so a "current maturity" for them would have to be re-dated forever.

| Artifact | Present | Current maturity |
|---|---:|---|
| `README.md` | Yes | The graded entry point: six-section academic report, quick start, gates, companion link |
| `docs/ACADEMIC_REPORT.md` | Yes | Long-form report — formalism, architecture decisions, measured results, three disclosed source contradictions |
| `docs/PRD.md` | Yes | Milestone goals, non-goals and acceptance, behaviour-free |
| `docs/PLAN.md` | Yes | M0-M9 gates with per-gate status, now held to `TODO.md` by `check_ledger_consistency.py` |
| `docs/TODO.md` | Yes | The single Thief-owned task ledger |
| `docs/PRD_commit_reveal.md` | Yes | SHA-256 commit-reveal, canonical bytes, and the post-game audit |
| `docs/PRD_scent_belief.md` | Yes | Scent physics, the public observation, and Thief-local belief |
| `docs/PRD_strategy.md` | Yes | Evasion policy and the survival baseline |
| `docs/PRD_p2p_mcp.md` | Yes | FastMCP peer roles and the negotiated wire |
| `docs/PRD_gatekeeper_reporting.md` | Yes | Rate limiting, report delivery and the JSON attachment |
| `docs/PRD_gui.md` | Yes | Local-truth GUI boundary |
| `docs/PRD_replay.md` | Yes | Verified/tampered replay semantics and the mandatory banner |
| `docs/SIM_WIRE_PROTOCOL.md` | Yes | The reference's actual wire, recorded separately from what the book requires (`C-022`) |
| `docs/JSON_ARTIFACT_SCHEMAS.md` | Yes | The four artifact shapes as emitted, held to the builders by `tests/unit/test_artifact_schema_doc.py` (`M1-025`) |
| `docs/ADR-0009-peer-launch.md` | Yes | Peer launch decision (sits beside `adr/` for historical reasons) |
| `docs/adr/README.md` | Yes | How ADRs are numbered and what each status means |
| `docs/SOURCE_OF_TRUTH.md` | Yes | The authority order every other document resolves against |
| `docs/SOURCE_INVENTORY.md` | Yes | What each source is and what it may be used for |
| `docs/SPECIFICATION_CONFLICTS.md` | Yes | `C-nnn` source contradictions and how each was resolved |
| `docs/UNKNOWN_REQUIREMENTS.md` | Yes | `U-nnn` open questions and what each blocks; `U-024`, `U-033`, `U-034` registered 2026-08-07 |
| `docs/REQUIREMENTS_LEDGER.md` | Yes | Requirements with their authority and test impact |
| `docs/PARAMETERS_BASELINE.md` | Yes | Appendix F values as Fixed / Minimum / Negotiable |
| `docs/SIMULATOR_BASELINE.md` | Yes | What the reference does, kept separate from what the book requires |
| `docs/BOOK_TEMPLATE_RECONCILIATION.md` | Yes | Where the book and the example templates disagree |
| `docs/SHARED_CONTRACT_POLICY.md` | Yes | How the shared bundle may change and who may accept a change |
| `docs/SHARED_REQUIREMENT_BASELINE.md` | Yes | Requirements both peers must satisfy identically |
| `docs/CONTRACT_HANDOFF_CHECKLIST.md` | Yes | What a contract handoff must carry before it can be accepted |
| `docs/CONTRACT_REVIEW.md` | Yes | Review of the candidate contract against the book |
| `docs/OPTION_B_INTEROP_DECISION.md` | Yes | The Option-B interoperability decision and its cost |
| `docs/INTERFACE_REVIEW.md` | Yes | The SDK surface and its import boundaries |
| `docs/VERIFICATION_POLICY.md` | Yes | What counts as evidence, and what may never be claimed without it |
| `docs/QUALITY_EVIDENCE.md` | Yes | Gate-by-gate evidence: ruff, coverage, file lengths, secrets, history scan |
| `docs/SELF_ASSESSMENT.md` | Yes | Grade self-assessment against the published rubric |
| `docs/REPOSITORY_AUDIT.md` | Yes | Structure and content audit against the book's chapter 9 requirements |
| `docs/SUBMISSION_CHECKLIST.md` | Yes | What must be true before the annotated tag is made (`scripts/check_submission_tag.py` checks the tag itself) |
| `docs/USAGE.md` | Yes | How to run the peer, the replay verifier and the gates |
| `docs/HANDOVER.md` | Yes | What a new maintainer needs to know first |
| `docs/RUNBOOK_reporting_setup.md` | Yes | Reporting setup, with credentials kept out of the repository |
| `docs/TEAM_INFO.md` | Yes | Group identifier, team code and members |
| `docs/PROMPT_LOG.md` | Yes | Historical provenance and correction entries |
| `docs/RESEARCH-REPORT-Performance-Analysis.md` | Yes | Measured performance study |
| `docs/ADR_STATUS_REVIEW.md` | Yes | A pass over every ADR status; kept because the statuses are deliberately unaccepted |
| `docs/DOCS_COMPLETENESS.md` | Yes | This table |
| `docs/adr/0001-mcp-contract.md` | Yes | MCP contract names. Pending |
| `docs/adr/0002-message-envelope-and-idempotency.md` | Yes | Message envelope and idempotency. Pending |
| `docs/adr/0003-schema-version-discrepancy.md` | Yes | Schema version `1.1` vs `1.2` (`C-008`). Pending — held rather than normalised |
| `docs/adr/0004-shared-json-private-toml.md` | Yes | Shared JSON / private TOML boundary. Pending — this is what keeps tunnel tokens out of negotiated files |
| `docs/adr/0005-scent-model.md` | Yes | Multiplicative scent against the reference's subtractive decay. Pending |
| `docs/adr/0007-llm-movement-policy.md` | Yes | LLM movement stays disabled, with rule 25's recommendation status preserved. Proposed |
| `docs/adr/0008-simulator-reuse-and-license.md` | Yes | Simulator reuse and licence. Pending |
| `docs/adr/0009-gui-truth-model.md` | Yes | GUI truth model. Proposed |
| `docs/adr/0010-gmail-reporting.md` | Yes | Gmail reporting. Proposed |

ADR statuses are `Pending`/`Proposed` on purpose. An unaccepted decision is recorded as
unaccepted; none is silently promoted, and `G-014` fails if one discussing supersession
does not record it. This document makes no cross-repository parity claim.
