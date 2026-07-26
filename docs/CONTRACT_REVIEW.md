# Independent Cop Contract Review

Review date: 2026-07-26

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
