# Documentation Completeness

Status: reviewed 2026-07-28. Supersedes the 2026-07-25 M0–M1 scaffold review, which
described a repository that no longer exists: it predated the M2 domain, the baseline
strategy, and three further Cop contract candidates.

Presence and content maturity are separate. A present document may remain gated where
contract or runtime evidence is unavailable.

| Artifact | Present | Current maturity | Completion gate |
|---|---:|---|---|
| Root `README.md` | Yes | M1 install/status guide | Add runtime usage and academic evidence after implementation |
| `docs/PRD.md` | Yes | M1 requirements and acceptance criteria | Expand only with confirmed or accepted behavior |
| `docs/PLAN.md` | Yes | Gated architecture plan and ADR index | Accept contract ADRs before protocol work |
| `docs/TODO.md` | Yes | Active owned/prioritized task ledger | Update status as gates pass |
| Contract review and handoff checklist | Yes | Original/revised candidates reviewed; provisional-copy inputs fail closed | Complete Stage A only from an explicit coordinator authorization |
| Book/template reconciliation | Yes | Book-confirmed rules separated from generated-example observations | Recheck against any authenticated Moodle templates or dated announcements |
| Proposed gate-resolution review | Yes | Simulator mechanics and supplied constants separated from coordinator acceptance | Update only after a pinned coordinator handoff or authenticated lecturer evidence |
| Mechanism PRDs | Yes | Confirmed boundaries plus open details | Close each mechanism's named unknowns |
| `docs/PROMPT_LOG.md` | Yes | Current through P-018; P-012–P-016 are reconstructed, not transcribed | Append significant AI-assisted work as it happens, not in arrears |
| `docs/ADR_STATUS_REVIEW.md` | Yes | Inventory of the ten ADRs: 7 `Pending`, 3 `Proposed`, 0 accepted | Decide the four locally decidable ADRs; the rest need external input |
| `docs/TEAM_INFO.md` | Yes | Identity confirmed 2026-07-28; `U-016` closed | Nothing outstanding |
| `pyproject.toml` / `uv.lock` | Yes | Independently installable M1 scaffold | Keep uv lock and metadata current |
| `src/` / `tests/` / `scripts/` | Yes | M2 core domain and the contract-independent baseline strategy behind the SDK; 139 tests at 99.36% branch coverage | Add protocol, runtime, and transport behavior through TDD after the contract gate |
| Thief conformance profile | No | Copy model superseded 2026-07-28 under `THIEF-002`; four Cop candidates were reviewed and none was ever copied. Checker remains `PENDING` | Author the profile (`M1-013`/`M1-014`), prove it against a neutral stub (`M1-015`–`M1-017`), then obtain profile acceptance |
| Active shared/private runtime config | No | Intentionally absent | ADR-0004 plus accepted contract |
| Runtime, GUI, replay, Gmail evidence | No | Out of M1 scope | Later gated milestones |

## Mechanism coverage

Dedicated PRDs exist for FastMCP, commit-reveal, scent/belief, Thief strategy,
gatekeeper/reporting, live GUI, and replay. Their acceptance criteria distinguish
confirmed outcomes from undecided payloads, formulas, ordering, providers, and layouts.
`PRD_strategy.md` is the only one describing implemented behavior; the rest remain
forward-looking.

## Known documentation debt

Presence is not currency. These are recorded rather than silently carried:

- No ADR is accepted. `PLAN.md` requires several to be settled before M2; M2 proceeded
  under the contract-independent carve-out instead. See `ADR_STATUS_REVIEW.md`.
- ADR-0004 and ADR-0005 have stale text — they predate `LS-002`, the `rate_limits`
  reclassification, and the scent-formula authority conflict recorded as finding N-4.
- No ADR references the Option B decision, although Option B proposes answers to
  ADR-0001, ADR-0002, and part of ADR-0006.
- `PROMPT_LOG.md` fell 17 commits behind before being reconstructed on 2026-07-28.

## Historical material

The archived 635-task document is historical coverage, not the active implementation
plan. Archived configs, translations, summaries, and simulator notes remain navigation
or provenance material and cannot override current direct evidence.

## Verdict

All local quality gates pass: ruff clean, 139 tests at 99.36% branch coverage, file
lengths and secret scan clean, and the shared-contract checker correctly fail-closed at
`PENDING` with exit 1. The M1 scaffold results remain in
[M1_VERIFICATION.md](M1_VERIFICATION.md).

The combined M1 gate still awaits provisional copy authorization, parity/conformance
evidence, and final contract freeze. The repository is not contract-frozen,
runtime-complete, submission-ready, or evidence complete.

Two documents describe work no longer confined to the M1 scaffold: `M2_DOMAIN.md` for
the core domain and `PRD_strategy.md` for the baseline policy. Both are
contract-independent by construction and neither advances the M1 gate.
