# PRD — Gatekeeper and Reporting

Status: **built**. This document described a future implementation until 2026-08-07; it now
describes the one in the repository. Where a stated intention and the built code disagreed,
the code was changed or the difference is recorded below under *Deliberate departures*.

## The pipeline, end to end

```
play → audit_series → agree → settlement_record
                                      │
        ┌─────────────────────────────┴──────────────────────────────┐
        │                                                            │
  build_declaration / build_config / build_log / build_result   compose_report
        │                    │                                       │
  validate_artifact     store_config                            gmail_wire.send_body
        │                (games/<game_id>/)                          │
  check_shared_game_uid                                        guard(gatekeeper)
        │                                                            │
  write_artifact (atomic)                                    users().messages().send
```

Rule 36 fixes the **order**: the comprehensive mutual audit is "a mandatory condition before
agreement on the JSON result". Two things enforce it rather than one, because a precondition
a caller can forget is not a precondition:

- `orchestration/settlement.agree(audit, ours, theirs)` takes the audit as its first
  argument, so agreement is unreachable without one.
- `reporting/email_report.compose_report(..., settlement=...)` requires the settlement
  record and refuses any state short of `agreed` with `audit_passed is True` (`M7-005f`).

## Confirmed requirements, and where each lives

| Requirement | Source | Built as |
| --- | --- | --- |
| External calls pass one gatekeeper | `PS-008` | `services/gatekeeper.guard` |
| 30 req/min, 2 concurrent, queue depth 100 | `AF-019` | `Gatekeeper` defaults |
| 5s before retry, 3 retries | `AF-019` | `send_report` backoff (5s, 10s, 20s — doubling) |
| 30s response, 60s watchdog | `AF-019` | `services/deadlines`, `services/watchdog` |
| Report is a JSON attachment, never body text | `AE-033`, `AE-034` | `compose_report` |
| Each peer reports separately after agreement | `AE-032` | `send_report` takes no opponent |
| Reports go to `rmisegal+uoh26finalgame@gmail.com` | `AF-020` | `REPORTING_ADDRESS` |
| OAuth scope is send-only | `AE-030` | `GMAIL_SEND_SCOPE` |
| Filenames derive from `game_id` | `AF-021` | `reporting/naming` |
| Four artifacts share one `game_uid` | `AR-001` | `check_shared_game_uid` |
| Commit hash in the declaration | `AE-053` | `build_declaration(github_commit=…)` |
| Tokens per game *and* per series | `AE-054` | `reporting/token_ledger` |
| Every game's config committed | Appendix F obligation 4 | `reporting/retention`, `games/` |
| Accurate count of games played | `AE-037`, `AE-038` | `reporting/league_ledger` |
| Nonces secret until the game ends | `AE-018` | `build_log` refuses without `ended_at` |

## Deliberate departures

**Validation is a table, not a JSON Schema** (`reporting/artifact_schema.py`). `U-019`
records that the four example artifacts prove only that the listed keys occur in the
inspected bytes — not requiredness, types, bounds or additional-property behaviour. A schema
generated from them would demand keys no source demands and then refuse a conformant
opponent, failing rule 36's mutual audit over a difference nothing forbids. Requiredness
therefore comes from the book, every required entry cites a rule or page, and unexpected keys
are accepted. The companion Cop repository solved the same problem the other way; both are
pinned as correct for their own repository rather than reconciled.

**`schema_version` is held at `1.1`** even though the required field set changed when rule
53's `github_commit` was added. Every inspected template shows `1.1` and `U-019` leaves that
provenance unresolved, so emitting an unobserved number invites a peer matching on `1.1` to
refuse our declaration. `M7-024`'s "visible, not silent" requirement is met by pinning a
digest of the required set instead (`test_artifact_schema_version.py`).

**`reporting/` imports no transport.** Artifact emission holds no socket and no peer state,
proved structurally from the AST rather than behaviourally, so a game abandoned because the
opponent vanished still writes its four files (`M7-023`). That game is the one whose evidence
gets disputed.

## Still open

Gmail draft-versus-send behaviour (`U-002`), the OAuth consent flow itself (`U-009`,
`M7-013`/`M7-013a` — deliberately unclaimed, since running consent is the operator's action
on their own machine), and template requiredness (`U-019`, ADR-0010).

The book requires separately submitted, mutually agreed JSON reports but does not establish
byte identity between the two independently delivered files. A populated template is not a
formal schema.

## Acceptance criteria, and the tests that hold them

- No external API bypasses the gatekeeper — `test_gatekeeper.py`, `test_external_gatekeeper.py`
- Limits, retries, timeouts configured rather than embedded — `test_limits.py`, `test_deadlines.py`
- Exactly the agreed JSON is attached, no free-text report — `test_gmail_wire.py`
- A report cannot be composed without a passed audit — `test_report_precondition.py`
- Wrong recipient, missing agreement, malformed artifact, secret leakage all fail —
  `test_email_report.py`, `test_artifact_schema.py`, `test_artifact_secrets.py`
- A full local series rehearses end to end, including a lost sub-game and a forged audit —
  `tests/integration/test_rehearsal*.py` (`M7-018`)
- External services are mocked; nothing in the suite opens a socket to a provider.
