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

> **Coordinator confirmation (2026-07-28):** the coordinator independently audited
> Cop main `be705f9` and issued `ACCEPTED_FOR_PROVISIONAL_PARITY: NO`, confirming the
> Thief's P0 on `config/game.json` (mixed stable/per-match configuration) and adding
> further semantic blockers, including that `rate_limits.json` should be treated as
> shared (reversing the Cop's local reclassification) and that role alternation must be
> marked `UNKNOWN`. Full record:
> [COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md).

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

## Candidate `0.2.0-proposed` review (2026-07-28)

Read-only inspection of the Cop bundle `shared_contract/` at immutable commit
`0c20bf03d916d7bbd9c7d4cfef87bd18e45e485d` (Cop branch
`agent/cop-m2-own-cell-barrier-fix`, not merged to Cop main). Every file was read with
`git cat-file blob <commit>:<path>` against the Cop object database. No file was
copied, edited, reformatted, or integrated into this repository.

This is Thief-side evidence prepared for the coordinator. It is not an authorization,
it does not complete any Stage A value, and it changes no gate.

### Independently reproduced integrity

| Check | Result |
|---|---|
| Controlled files declared in `PARITY_MANIFEST.json` | 32 |
| Files present under `shared_contract/` in the tree | 33 (manifest correctly excludes itself) |
| Per-file SHA-256 recomputed from raw blobs | **32/32 match** |
| Manifest exact-byte self-hash | `2b473b53…09642` **match** |
| CRLF bytes in any controlled blob | none |
| `vectors/move-commit.vectors.json` reproduced | **4/4** |
| `vectors/config-sha256.vectors.json` reproduced | **3/3** |
| `negotiation_terms.projection.json` `game_object` hash | `259a214a…24c15` **match** |

Integrity was never the disputed question and it passes again. A clean manifest proves
only that the declared bytes are the actual bytes; it proves nothing about semantics.

### Verdict

**CONTRACT INTEGRATION: NO-GO**

**M2 GAMEPLAY: NO-GO**

Of the seven coordinator blockers of 2026-07-28: one is resolved, one is partially
resolved, one is substantially improved but incomplete, and four are unresolved. Two
new P0 defects that were not present in `e0df5ba` were found.

### Status against the seven coordinator blockers

| # | Coordinator blocker | Status | Basis |
|---|---|---|---|
| 1 | Stable contract mixed with per-match identity/configuration | **RESOLVED** | The bundle contains no active match. `fixtures/match_config.example.json` is framed as a template, the per-match object is supplied at runtime, and `README.md` states that changing opponent IDs never edits a bundle file. No controlled file carries a runtime identity. |
| 2 | Schema requires unsupported root fields | **NOT RESOLVED (P0)** | `schemas/match-config.schema.json` still lists `version` and `extensions` in `required` under `additionalProperties: false`. An opponent sending the exact Appendix B structure is still rejected. The required Appendix-B-exact conformance fixture does not exist in `fixtures/`. |
| 3 | `rate_limits.json` classification | **PARTIALLY RESOLVED (P1)** | Gatekeeper values now sit inside the match object and are therefore covered by the `config_sha256` lock, satisfying "include its agreed values in the match lock". But the separate shared `rate_limits.json` that Appendix B describes is silently absent, with no stated mapping and no defined handling if an opponent sends one. `response_timeout_sec`/`watchdog_timeout_sec` are split into `network_and_league` while the other five Gatekeeper values sit in `rate_limiter_gatekeeper`; `AF-019` groups all seven together, and the split has no cited authority. |
| 4 | Role alternation presented as binding | **NOT RESOLVED (P0)** | `SHARED_RULES.md` still contains a normative "Role alternation" section asserting odd-natural/even-opposite alternation as fact, with no `UNKNOWN` marking and no authority citation. The coordinator required its removal from normative contract documents. This directly contradicts Thief `LS-001` (`UNKNOWN`) and reopened `U-021`. |
| 5 | Canonical hashing insufficiently established | **IMPROVED, INCOMPLETE (P1)** | Real progress: three hash domains are cleanly separated and 7/7 declared vectors reproduce exactly in an independent Thief-side implementation. Remaining gaps below. |
| 6 | Unknown-opponent interoperability unproven from the book | **NOT RESOLVED — needs a coordinator ruling** | The bundle is honest that it is Option-B/`PROPOSED` pinned to the simulator, but that does not discharge "prove from the official book". The coordinator's specific required changes are unmet: schemas carry no stable `$id`, no capability/version negotiation exists, and `PROTOCOL_PROFILE.md` explicitly forbids `protocol_version`. See the open question below. |
| 7 | Cross-field configuration validation incomplete | **NOT RESOLVED (P0)** | `$defs/coordinate` is still any two integers with no bounds. `axis_start_index` is still an unbounded integer accepting negatives — the identical defect flagged against `game-config.schema.json`. `axis_origin_corner` is a free string with `minLength: 1` and no enum, so any value validates. Nothing validates `thief_start`/`cop_start` against `grid_size`, the origin corner, or the start index; nothing prevents both agents starting on the same cell. No post-schema semantic-validation step is documented anywhere in the bundle. |

### Remaining canonicalization gaps (blocker 5)

- **No escaping vector.** The coordinator required vectors covering "Unicode, escaping,
  nested objects and numbers". Nested objects, numbers (`2.5`, `0.1`) and non-ASCII
  passthrough (Hebrew) are covered; **escaping is not**. No vector exercises a quote,
  backslash, control character, solidus, or non-BMP/surrogate-pair codepoint.
- **Reproduction is single-language.** The vectors reproduce exactly, but the profile is
  specified as Python `json.dumps` keyword arguments and was reproduced here in Python.
  That is not cross-language evidence. Float rendering is the concrete risk.
- **`signature` is required but undefined.** `schemas/negotiate.schema.json` requires a
  `signature` string, and `MATCH_CONFIGURATION.md` requires offers to match before play,
  but no controlled file defines the signature algorithm, key handling, signed byte
  range, or verification rule. `negotiate.valid.json` carries the literal placeholder
  `"ed25519:example-signature-placeholder"`. `U-002` remains open on exactly this point.

### New P0 and P1 defects found in this candidate

**N-1 (P0) — `SHARED_RULES.md` states a barrier rule that contradicts both peers.**
The rules table reads: "A barrier occupies one cell **exactly one orthogonal step from
the placing peer**". That wording excludes the placing peer's own cell. Book §3.4 (PDF
p.37 / printed p.21) permits placement on the peer's own current cell *or* one
orthogonally adjacent cell. Thief M2 implements own-cell-or-one-step (`42bc571`), and
the Cop's own code fix in this very commit does the same. Copying this bundle would
import normative prose forbidding what both implementations do. The Cop's own handoff
lists this as an open blocker, so it is known and simply not yet fixed.

**N-2 (P0) — the per-sub-game `links` pattern is a placeholder used as a regex.**
`schemas/per-subgame-config.schema.json` constrains `links.config` and `links.log` with
`"pattern": "g<NN>"`. That regex matches the literal text `g<NN>` and nothing else.
Verified against the pattern: `config_demo-series_g<NN>.json` is **accepted**, while the
real filenames `config_demo-series_g01.json` and `config_demo-series_g1.json` are both
**rejected**. `per_subgame_config.valid.json` passes only because it carries the
unfilled placeholder. As written the schema accepts unfilled templates and rejects every
real artifact, contradicting the confirmed `AF-021` filename patterns.

**N-3 (P1) — the projection fixture contradicts the bundle's own `config_sha256` rule.**
`MATCH_CONFIGURATION.md` states that `config_sha256` covers the "complete parsed
per-match shared game object" and "must include the actual agreed `agreed_between`
values". `fixtures/negotiation_terms.projection.json` computes
`game_object_config_sha256` over an object missing seven of the eleven required roots,
including `agreed_between`, `scoring`, `pheromones`, `rate_limiter_gatekeeper`,
`version`, `world`, and `extensions`. The only worked example of the mapping
demonstrates the rule being broken.

**N-4 (P2) — scent formula authority.** `SHARED_RULES.md` cites "Book Ch.4; ADR-005" for
`tau_ij(t+1) = max(0, (1-rho) * tau_ij(t) + delta_tau_ij)`. Thief `AF-016` records the
three scent constants as `CONFIRMED` but explicitly notes "Formula and schema remain
unknown". Either the Cop holds a citation the Thief ledger lacks, or the authority claim
overstates. This must be reconciled before either peer implements M6.

**N-5 (P2) — `verify.py` cannot represent a frozen bundle.** `build_manifest` hardcodes
`"freeze_status": "proposed_unfrozen"`, and `verify()` fails if the stored manifest
differs from the recomputed one. A future `CONTRACT_FREEZE: GO` therefore requires
editing a controlled file, which changes its hash and the manifest self-hash. This is a
forward-compatibility snag for the freeze step, not a defect today.

**N-6 (P2) — `schema_version` compatibility still unresolved.** `const: "1.2"` continues
to reject `1.1` and `1.3`, and the schema description admits compatibility "is
unresolved". Carried over unchanged from the previous review.

### Genuine improvements over `e0df5ba`

| Earlier finding | Status in `0.2.0-proposed` |
|---|---|
| `config/game.json` embeds match-specific participant IDs in a parity-controlled file (Thief P0, coordinator blocker 1) | **Resolved.** No active match in the bundle; the example is a template in `fixtures/`. |
| Checker is Cop-specific: Cop-only `--write`/`write_manifest`, hardcoded Cop paths, "Cop-local contract integrity OK" messaging (Thief required outcome 3) | **Resolved.** `verify.py` discovers files by `rglob` under the bundle root, never writes, has no role-specific paths or wording, and works identically from a Thief root. Manifest generation is moved out to an owner-only tool. |
| Hash domains conflated | **Resolved.** Move-commit, `config_sha256`, and `config_file_sha256` are separately defined, separately vectored, and explicitly distinguished from the manifest self-hash. |
| No protection against private-truth leakage in public messages | **Improved.** `turn-message.schema.json` adds a `not`/`anyOf` guard rejecting `position`, `move`, `nonce`, `intent`, and `verdict`. Note that `additionalProperties: true` still permits differently named leakage fields. |

### Required revision outcomes

1. Remove `version` and `extensions` from `required`, and add a fixture proving an exact
   Appendix B object is accepted (blocker 2).
2. Remove the normative role-alternation section from `SHARED_RULES.md` and mark it
   `UNKNOWN` pending an authenticated lecturer answer (blocker 4).
3. Correct the `SHARED_RULES.md` barrier sentence to own-cell-or-one-orthogonal-step so
   the contract matches book §3.4 and both implementations (N-1).
4. Replace the `g<NN>` placeholder pattern with a real expression such as
   `^config_.+_g\d{2}\.json$`, and refixture with a filled filename (N-2).
5. Add bounds and cross-field validation: bound `axis_start_index`, enumerate
   `axis_origin_corner`, and validate both start coordinates against `grid_size`, the
   origin corner, and the start index, with rejection tests (blocker 7).
6. Add escaping vectors and at least one non-Python reproduction, or explicitly scope the
   canonicalization profile as Python-defined (blocker 5).
7. Define the `signature` algorithm and verification rule, or remove `signature` from
   `required` until it is defined (N-3 companion).
8. Correct the projection fixture so `config_sha256` is computed over a complete object
   (N-3).
9. Document the relationship between the nested Gatekeeper block and the Appendix B
   `rate_limits.json`, including behaviour when an opponent sends the separate file
   (blocker 3).

### Open question for the coordinator

Blocker 6 asks for interoperability proven from the official book, while the accepted
Option-B decision deliberately selects a simulator-pinned profile for details the book
leaves open. These pull in opposite directions and the Thief cannot resolve the tension
on its own. The coordinator should state explicitly whether accepting Option B discharges
blocker 6, or whether blocker 6 additionally requires stable schema `$id`s, a capability
or version negotiation mechanism, and conformance evidence against a peer that shares
none of these 32 files. Nothing in this repository may assume either answer.

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
