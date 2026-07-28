# Independent Cop Contract Review

Initial review date: 2026-07-26

Latest review update: 2026-07-28

## Revised-candidate update

The original path-by-path review below remains the historical review of immutable Cop
candidate `84339c210c8e3293d972bccec5912abf519d502c`.

The Thief independently inspected immutable revised candidate
`b586af9e55dcc40789a1d7ab683edb97c8cfabc6` and compared it with
`COORDINATOR_M1_CANDIDATE_REVIEW.md`. The revised candidate fixed several original
defects:

- it represents `agreed_between`, match identity, and selected match values;
- it distinguishes local integrity from optional cross-root comparison;
- it adds neutral match validation and negative mutation tests;
- it corrects source priority and generated-artifact provenance;
- its 17-file local manifest and quality gates passed coordinator review.

It remained ineligible for Thief copying because:

- parity-controlled `config/game.json` and `config/rate_limits.json` embed one
  permanent neutral match instance, so new opponents would mutate frozen bytes;
- controlled checker messages and private-configuration prose are Cop-specific rather
  than role-neutral;
- it does not prove two different valid opponent/match identities can be supplied
  without changing controlled stable-contract files;
- the coordinator explicitly recorded `ACCEPTED_FOR_THIEF_COPY: NO`,
  `CONTRACT_FREEZE: NO-GO`, and `M2_GAMEPLAY: NO-GO`.

`665bd30a75866e872f899eb337664266e26129ed` was previously described as local-only.
It has since been pushed to the remote `agent/cop-m1-contract-revision` branch and
merged to Cop main via PR #8. Two further commits followed it on that branch:
`459cd73` (moved `config/rate_limits.json` and its schema to the local tier, reducing
the controlled set from 20 to 18 paths) and `e0df5ba530fd7c433d41a98c5976ca7e08cdfa53`
(documented the candidate as technically ready for external coordinator review, with
status `UNFROZEN — NO-GO UNTIL PARITY`). The Cop main HEAD is now
`be705f9dc9e14b9fc8a53ffe1658493ad977f1fc` (2026-07-28 merge). Those commits and
their exact proposed values must not be copied or relabeled as accepted; no coordinator
verdict supplies `ACCEPTED_FOR_PROVISIONAL_PARITY: YES` for any of them. The
proposed inventory for `e0df5ba` is recorded in
[GATE_RESOLUTION_REVIEW.md](GATE_RESOLUTION_REVIEW.md).

The corrected handoff sequence is provisional copy authorization, exact-byte
parity/conformance testing, external-decision closure, and only then final freeze.
Requiring final freeze before any provisional copy would create a circular gate.

**CURRENT CONTRACT INTEGRATION: NO-GO**

**CURRENT M2 GAMEPLAY: NO-GO**

## Candidate e0df5ba review (2026-07-28)

Read-only inspection of `e0df5ba530fd7c433d41a98c5976ca7e08cdfa53` (Cop main
`be705f9`, merged via PR #8). Every file was read using
`git show e0df5ba:<path>`. No file was copied or modified.

### Verdict

The candidate makes substantial progress over `b586af9`: `config/rate_limits.json`
is correctly moved to the local tier, `agreed_between` is present and required in
the schema, the checker now supports genuine cross-root comparison via
`--compare-root`, and all Appendix F values are implemented with correct
fixed/minimum/negotiated semantics. However, one P0 remains: `config/game.json`
contains match-specific participant identifiers that must change per actual match,
which means controlled bytes cannot stay frozen across different real-participant
match instances. Stage B requirement — "Two different valid participant/match pairs
work without changing any controlled stable-contract byte" — cannot be verified from
this design.

**CONTRACT INTEGRATION: NO-GO**

**M2 GAMEPLAY: NO-GO**

### Path-by-path review

| Candidate path | Severity | Independent review |
|---|---|---|
| `.gitattributes` | P1 | Deterministic LF rules for all 18 controlled paths. Content is correct and internally consistent. Making `.gitattributes` a cross-repository parity-controlled file is a project policy choice, not a book requirement. |
| `config/game.json` | P0 | All Appendix F values are present with correct fixed/minimum/negotiated semantics. `agreed_between` correctly requires two participant identifiers. **P0: The file contains `"neutral-group-alpha"` and `"neutral-group-beta"` as placeholder participant IDs. Because the file is listed as a parity-controlled stable file (exact bytes identical between repos), any actual match with real group IDs would require mutating those controlled bytes. The candidate demonstrates schema correctness using a neutral fixture but does not define the mechanism by which two different real-participant match instances produce byte-identical `config/game.json` without editing the controlled source. Stage B checklist item "two different valid participant/match pairs work without changing any controlled stable-contract byte" is not satisfiable under the current design.** |
| `docs/contracts/ARTIFACT_CONTRACT.md` | P1 | Correctly defines four artifact families, common identity (`game_id`, `game_uid`, `links`), the config lock, and declaration requirements. Role alternation (odd-game natural, even-game opposite) is documented as owner-supplied lecturer direction dated 2026-07-27, not directly book-confirmed. UUID protocol (UUIDv4 vs. SHA-256-derived) remains open for M7. |
| `docs/contracts/CONTRACT_VERSION` | PASS | Reads `0.1.0-proposed`. Accurately reflects the unfrozen candidate state. |
| `docs/contracts/LEAGUE_CONTRACT.md` | P1 | Clear separation of fixed, minimum, and negotiated values, each with a direct Appendix F locator. Role alternation cited as owner-supplied direction rather than direct book text. |
| `docs/contracts/MATCH_CONFIGURATION.md` | P1 | Canonical hash algorithm (sorted keys, compact separators, unescaped Unicode, UTF-8) is clearly defined and aligned with `CR-001`. `config_sha256` scope is correctly separated from source bytes. Does not define the mechanism for producing an identical `config/game.json` with non-placeholder participant IDs across two independent repositories. |
| `docs/contracts/PRIVATE_CONFIGURATION.md` | PASS | Correctly enumerates all private-tier concerns. `config/rate_limits.json` correctly classified as local. No parity claim for private data. |
| `docs/contracts/SHARED_RULES.md` | P1 | All mandatory rules carry direct book citations. Schema and extension decisions correctly marked as proposals. Role alternation and `game.version` root placement are PROPOSED without direct book authority. |
| `docs/schemas/artifact-keyset-fixture.schema.json` | P1 | Correctly labeled `LOCAL_OBSERVATION_NEEDS_MANUAL_REVIEW`. Validates fixture metadata structure only, not official artifact content. Provenance of the four source files remains unverified. |
| `docs/schemas/config-hash-vector.schema.json` | PASS | Defines the hash-vector structure cleanly. Consistent with `CR-001`. Provides a deterministic schema for the canonical-hash test vector. |
| `docs/schemas/game-config.schema.json` | P1 | Material improvement: `agreed_between` is now present and required; all Appendix F values use correct `const`/`minimum` constraints. `schema_version: "1.2"` `const` rejects 1.1/1.3 without an accepted compatibility policy. `axis_start_index` has no bounds preventing negative values. `additionalProperties: false` at the root is a project proposal. |
| `scripts/check_shared_contracts.py` | P1 | `--compare-root` flag enables genuine cross-root exact-byte comparison, directly resolving the original P1 about Cop-local-only integrity. **P1: Docstring says "Cop-authored contract bundle"; success message says "Cop-local contract integrity OK". When copied to Thief, the `--write` flag would write a manifest derived from the Thief root, producing incorrect results. Thief usage must be restricted to the verify/compare paths only; the write path is not role-neutral.** |
| `scripts/shared_contract_integrity.py` | P1 | `compare_repository_roots` enables genuine cross-root byte comparison — a significant improvement. `write_manifest` is a Cop-only operation: it builds the manifest from the local root and would produce incorrect output from the Thief root. `controlled_paths` hardcodes Cop paths and would return empty or wrong results from a fresh Thief root before copying. The write/build paths are not role-neutral. |
| `tests/fixtures/contracts/agreed_config.keyset.json` | P1 | Correctly labeled `NEEDS_MANUAL_REVIEW`. Records observed key sets including `agreed_between`, `config_sha256`, `game_uid`, and `sub_game_number`. All values redacted; only key presence is claimed. Provenance remains unverified (simulator-generated). |
| `tests/fixtures/contracts/declaration.keyset.json` | P1 | Correctly labeled `NEEDS_MANUAL_REVIEW`. Records observed key sets including `signature`. Required/optional status of `signature` and its generation mechanism remain unknown. Provenance unverified. |
| `tests/fixtures/contracts/final_result.keyset.json` | P1 | Correctly labeled `NEEDS_MANUAL_REVIEW`. Records `mutual_agreement.sha256` and `confirmed` observations. Sub-game roles use a wildcard key pattern consistent with the proposed alternation model. Provenance unverified. |
| `tests/fixtures/contracts/game-config-sha256.vector.json` | PASS | Canonical hash vector for the neutral `config/game.json` fixture: 965 UTF-8 bytes, SHA-256 `adac9efe...`, sorted-compact-unescaped-Unicode-UTF-8 algorithm. Independently verifiable deterministic test vector. |
| `tests/fixtures/contracts/game_log.keyset.json` | P1 | Correctly labeled `NEEDS_MANUAL_REVIEW`. Records commit-reveal structure (payload/nonce/commit) and Step-0 system-spec keys. Provenance unverified. |

### Improvements over b586af9

| b586af9 finding | e0df5ba resolution |
|---|---|
| `config/rate_limits.json` embeds a neutral match instance as a parity-controlled file | Resolved: `rate_limits.json` and its schema moved to the local tier and excluded from parity |
| Checker proves only Cop-local integrity | Resolved: `--compare-root` adds genuine cross-root exact-byte comparison |
| `agreed_between` absent from schema; closed schema rejects it | Resolved: `agreed_between` is now present and required |
| Checker messages say "Shared-contract parity OK" without cross-root comparison | Resolved: messages now distinguish local-verify from cross-root compare |
| `config/game.json` and `config/rate_limits.json` embed one permanent neutral match instance so new opponents would mutate frozen bytes | Partially resolved: `rate_limits.json` removed; `config/game.json` still embeds placeholder participant IDs (P0 remains for the config file) |
| Cop-local integrity labeled as parity | Resolved: cross-root comparison function added |

### Required revision outcomes

1. **Resolve the stable-contract mutation gate.** Define whether `config/game.json`
   is (a) a stable template (participant IDs appear only in emitted artifacts, not in
   the source constitution) or (b) a per-match file regenerated by mutual agreement.
   If (b), specify the negotiation mechanism and clarify that the parity manifest is
   also per-match.
2. **Prove two different real-participant match identities** produce byte-identical
   `config/game.json` values without editing any currently parity-controlled stable
   file.
3. **Clarify Thief checker usage boundaries.** Specify which paths of
   `check_shared_contracts.py` and `shared_contract_integrity.py` are valid from a
   Thief root, and mark or remove the Cop-only `--write` / `write_manifest` path.
4. **Confirm role alternation** through a direct book citation or explicit
   coordinator acceptance of the owner-supplied direction.
5. **Resolve schema version compatibility.** Define an accepted policy for
   `schema_version: "1.1"`, `"1.2"`, and `"1.3"`, or provide a compatibility
   normalization rule.

## Scope and method

This is a read-only Thief-side review of the immutable Cop candidate at
`84339c210c8e3293d972bccec5912abf519d502c`. Every finding below comes from Git
objects addressed as `<commit>:<path>`, not from the mutable Cop working tree. No
candidate file was copied, edited, reformatted, generated, or integrated into this
repository.

Candidate label: `0.1.0-proposed`

Candidate freeze status: `proposed_unfrozen`

Coordinator verdict: rejected pending revision

Thief integration result: zero accepted controlled files

## Verdict

The candidate is not a complete public contract or negotiated per-match configuration.
It cannot bind two actual participants to one game/sub-game, does not define the bytes
covered by `config_sha256`, and does not demonstrate compatibility with a neutral
unknown opponent. Its checker proves Cop-local bundle integrity only.

**CONTRACT INTEGRATION: NO-GO**

**M2 GAMEPLAY: NO-GO**

## Findings by severity

### P0 — blocking

1. **Participant and match binding are absent.** `config/game.json` and its schema omit
   `agreed_between`, opponent identities, `game_id`, `game_uid`, `sub_game_number`,
   `config_name`, and `config_sha256`. The active object therefore cannot represent
   the agreed, uniquely named configuration for a particular match.
2. **Stable, default, negotiated, and private concerns are not separated.** Fixed
   league semantics, minimums, negotiation defaults, and selected values are stored in
   permanent repository files. No deterministic proposal/acceptance process produces
   a per-match agreement, and no implemented overlay establishes the private boundary.
3. **Canonicalization and hash scope are unresolved.** The candidate does not specify
   raw versus semantic bytes, self-hash exclusion, encoding, Unicode normalization,
   numeric rendering, key/array ordering, whitespace, duplicate-key handling, or
   error semantics. Its manifest canonicalization does not define `config_sha256`.
4. **Artifact provenance is unverified.** The four fixture sources are described as
   supplied examples, but the coordinator found their bytes identical to locally
   generated simulator logs. They are observations pending authentic
   Moodle/lecturer provenance, not binding official templates.
5. **Cross-repository parity is absent.** The candidate manifest describes 13 Cop
   paths. At review time Thief has 0/13 byte matches: 11 paths are absent and the two
   same-named paths differ. No accepted handoff exists.

### P1 — major

1. **Unsupported strict-schema decisions reject plausible compliant data.**
   `additionalProperties: false` appears at the root and major nested objects.
   `agreed_between` is consequently rejected even though Appendix B provides strong
   evidence for participant agreement. The schemas use invented `example.invalid`
   identifiers and enforce a project-selected two-file layout.
2. **Schema versions are unresolved.** Book example `1.2`, generated-example `1.1`,
   simulator `1.3`, contract `0.1.0-proposed`, and configuration revision `1.00` are
   not governed by an accepted compatibility rule.
3. **The configuration/Gatekeeper split is only a proposal.** Appendix B and the
   generated example place Gatekeeper data in the agreed configuration, while the
   candidate moves it to `config/rate_limits.json` and relocates response/watchdog
   values. Hash and agreement scope across the files is undefined.
4. **Validation is strict about shape but incomplete about meaning.** Coordinate
   bounds, nonnegative hint/token values, and positive response/watchdog timeouts are
   not fully enforced, while unproven extensions are rejected.
5. **Unknown-opponent compatibility is untested.** There is no neutral participant
   fixture, version negotiation, party-ordering rule, bidirectional offer/accept test,
   match mismatch procedure, or cross-process conformance test.
6. **Cop-local integrity is labeled as parity.** The checker accepts one repository
   root, compares it with that root's own manifest, and prints
   `Shared-contract parity OK`. It does not inspect Thief, compare a second root, or
   verify the manifest's separately supplied self-hash.

## Path-by-path review

| Candidate path | Severity | Independent review |
|---|---|---|
| `.gitattributes` | P1 | Deterministic LF rules are useful, but making a repository-global attributes file parity-controlled is a candidate policy choice and has not been accepted. |
| `config/game.json` | P0 | Contains fixed values, minimums, and negotiation defaults as one static profile. It lacks participant, match, sub-game, unique-name, agreement-hash, and selected-negotiation semantics. |
| `config/rate_limits.json` | P1 | Uses an unaccepted second shared document, mixes minimums with negotiation defaults, and gives no deterministic relation to the per-match configuration hash. |
| `docs/contracts/CONTRACT_VERSION` | P0 | Correctly says `0.1.0-proposed`; it is not an accepted/frozen contract version. |
| `docs/contracts/SHARED_RULES.md` | P0 | Explicitly unfrozen, but uses the wrong source order, overstates generated-example provenance, and mixes direct requirements with proposed field names, versions, layout, and parity policy. |
| `docs/schemas/artifact-keyset-fixture.schema.json` | P1 | Validates only descriptor metadata. Its `example.invalid` ID, closed-object policy, `1.1` constant, and “supplied example” provenance are not authoritative artifact constraints. |
| `docs/schemas/game-config.schema.json` | P0 | Omits match binding and rejects it through closed objects. It freezes unresolved version/layout decisions and accepts some semantically invalid coordinates and negative/unbounded negotiated values. |
| `docs/schemas/rate-limits.schema.json` | P1 | Freezes the proposed split and second `1.2` document. Response and watchdog values lack positive bounds; extension rejection is unsupported. |
| `scripts/check_shared_contracts.py` | P0 | Proves only Cop-local bytes match a Cop-local manifest. It has no cross-root comparison or accepted handoff inputs and does not validate negotiated config bytes. |
| `tests/fixtures/contracts/agreed_config.keyset.json` | P0 | Observes `agreed_between`, identifiers, `config_name`, and `config_sha256`, exposing their absence from the active config/schema. Source provenance remains unverified. |
| `tests/fixtures/contracts/declaration.keyset.json` | P1 | Records generated-example keys only. It cannot establish required identity, repository, MCP URL, model, hardware, or signature fields. |
| `tests/fixtures/contracts/final_result.keyset.json` | P1 | Records generated-example result keys only. Role scheduling and formal requiredness remain unresolved. |
| `tests/fixtures/contracts/game_log.keyset.json` | P1 | Records generated-example payload/nonce/commit keys only. It supplies no canonicalization, sequencing, or binding semantics. |
| `docs/contracts/PARITY_MANIFEST.json` | P0 | Excludes itself and lists a candidate-controlled scope. Its separate exact-byte hash and all per-file hashes require an accepted coordinator handoff before Thief may trust or copy its paths. |

## Required revision outcomes

A future Cop candidate must, before coordinator acceptance:

- separate stable league semantics, negotiated per-match values, and private peer data;
- bind both actual participants and the required match/sub-game identity;
- resolve or explicitly block schema-version compatibility;
- define exact canonical bytes and `config_sha256` scope with test vectors;
- distinguish local integrity from actual cross-repository comparison;
- treat generated JSON examples as non-authoritative until provenance is authenticated;
- avoid unsupported closed-schema and opponent-specific assumptions;
- pass bidirectional conformance against a neutral compliant-opponent fixture.

Until those outcomes are reviewed and the full handoff is supplied, Thief must keep its
existing checker fail-closed and must not begin contract integration or gameplay.
