# Coordinator M1 Contract Verdict — 2026-07-28

## Verdict

**`ACCEPTED_FOR_PROVISIONAL_PARITY: NO`**

Audited Cop main at commit `be705f9dc9e14b9fc8a53ffe1658493ad977f1fc`
(candidate tip `e0df5ba530fd7c433d41a98c5976ca7e08cdfa53`).

The manifest SHA-256 is
`473982dc01594b1c7abee8fc7f20cf665a6b245e53114ed4a2732c115a35d86a`. All 18 recorded
file hashes are correct. **The rejection is semantic, not an integrity or CI failure.**

This is the authoritative coordinator decision. It supersedes any Cop self-declaration
of readiness and any unauthenticated course-material or simulator-derived assertion.
No shared file may be copied into Thief. `CONTRACT_FREEZE` and `M2_GAMEPLAY` remain
`NO-GO`. The Cop must revise and issue a new commit and manifest before Thief copying
or gameplay may be reconsidered.

## Blocking issues and required changes

### 1. Stable contract and per-match configuration are still mixed

`config/game.json` contains placeholder participants (`neutral-group-alpha`,
`neutral-group-beta`) and one fixed hash. Officially, `agreed_between` and negotiated
values must represent the two actual opponents in each match.

Required changes:
- Move the neutral configuration to a test-fixture/template path.
- Do not treat its SHA-256 as the universal runtime configuration hash.
- Generate and retain a distinct configuration for each opponent/match.
- Validate an opponent's configuration against stable rules, then agree on and lock
  the resulting exact bytes.
- Separate repository-contract parity from per-match configuration parity.

> This corroborates the Thief's independent P0 finding on `config/game.json` recorded
> in [CONTRACT_REVIEW.md](CONTRACT_REVIEW.md) (candidate `e0df5ba` review).

### 2. The schema requires unsupported fields

The candidate requires root fields `version: "1.00"` and `extensions`, although
Appendix B's official `game.json` structure does not contain them. With
`additionalProperties: false`, an unknown opponent following the official example can
be rejected.

Required changes:
- Remove these fields from the mandatory official profile.
- Keep the internal contract version outside the played configuration, or make
  `extensions` optional through an explicitly negotiated profile.
- Add a conformance fixture using the exact Appendix B structure and prove it is
  accepted.

### 3. `rate_limits.json` is incorrectly classified as local-only

Appendix B describes `rate_limits.json` as shared, signed and exchanged JSON. The
candidate excludes it from parity and permits private extensions based on simulator
behavior and an unauthenticated clarification.

Required changes:
- Until an authenticated lecturer clarification explicitly supersedes the book, treat
  `rate_limits.json` as shared match configuration.
- Include its agreed bytes or canonical values in the match lock.
- Put purely local enforcement settings in TOML or a separately named local file.
- Ensure local settings cannot weaken the signed values.

> Note: this reverses the direction taken in the `459cd73` Cop commit, which moved
> `rate_limits.json` to the local tier.

### 4. Role alternation is presented as binding without sufficient official evidence

Odd-natural/even-opposite alternation is confirmed by the simulator, but not by the
supplied official project book. The recorded "lecturer direction" is explicitly **not**
an authenticated Moodle announcement or original lecturer message.

Required changes:
- Remove role alternation from normative contract documents for now and mark it
  `UNKNOWN`.
- Obtain an authenticated lecturer answer.
- If alternation is confirmed, prove both repositories can execute both roles.
- If repositories remain role-specific, remove the opposite-role requirement.

> Thief action: this reopens `U-021`. The `LS-001` ledger entry that briefly marked
> alternation `CONFIRMED` (from unauthenticated course material) is reverted to
> `UNKNOWN`. See [REQUIREMENTS_LEDGER.md](REQUIREMENTS_LEDGER.md) and
> [UNKNOWN_REQUIREMENTS.md](UNKNOWN_REQUIREMENTS.md).

### 5. Canonical hashing is not sufficiently established for unknown implementations

The candidate freezes compact JSON with unescaped Unicode. The official book confirms
sorted-key canonicalization but does not fully define Unicode escaping or cross-language
number serialization.

Required changes:
- Obtain an authoritative canonicalization rule or official hash vector.
- Define a named canonicalization profile.
- Add cross-language vectors covering Unicode, escaping, nested objects and numbers.
- Do not freeze the current algorithm as official before those vectors agree.

> Consistent with the still-open `U-002`; `CR-001` settles only sorted-compact-UTF-8
> for the shown commit payload.

### 6. Unknown-opponent interoperability cannot yet be confirmed

MCP tool names, message envelopes, protocol-version negotiation, idempotency, error
formats, commit-reveal encoding and complete artifact schemas remain unresolved or
deferred. Exact parity between the two teammate repositories does not prove
compatibility with a classmate's independent implementation.

Required changes:
- Define a minimal public interoperability profile or capability-negotiation mechanism.
- Give schemas stable identifiers and explicit compatibility rules.
- Add a reference-compatible adapter without making simulator-specific names the only
  option.
- Run conformance tests against an independent peer that does not share the 18
  repository files.

> Consistent with still-open `U-003`.

### 7. Cross-field configuration validation is incomplete

Coordinates are accepted as any pair of integers without verifying that they lie inside
the negotiated board or correspond to the negotiated axis origin/index.

Required changes:
- Add semantic validation after JSON Schema validation.
- Validate both starting positions against grid size, axis origin and starting index.
- Add rejection tests for invalid coordinates and unsupported coordinate conventions.

## Consequence for Thief

- Stage A of [CONTRACT_HANDOFF_CHECKLIST.md](CONTRACT_HANDOFF_CHECKLIST.md) remains
  incomplete: the coordinator provisional verdict is now an explicit `NO`.
- No controlled file is copied; the contract checker stays fail-closed (`PENDING`,
  exit 1).
- M1-007 through M1-012 remain `BLOCKED`; M2–M9 remain `BLOCKED ON M1`.
- The single next authorized action is external: the Cop revises the contract per the
  seven issues above and issues a new immutable commit and manifest, after which the
  coordinator re-reviews for a possible `ACCEPTED_FOR_PROVISIONAL_PARITY: YES`.
