# Proposed Cryptographic and Configuration Gate Resolution Review

Review date: 2026-07-27; updated: 2026-07-28

## Verdict

The supplied direction contains useful book requirements and accurate observations
about lecturer-simulator v3.0.0, but it does not provide a coordinator-approved Cop
handoff. It also supplies one historical simulator commit and two hashes that are
absent from the inspected JSON files.

**CONTRACT INTEGRATION: NO-GO**

**M2 GAMEPLAY: NO-GO**

No Cop-owned shared file was copied or modified during this review.

## Exact-value verification

| Supplied value or claim | Verified result |
|---|---|
| Approved Cop commit `7cf3fc9` | Not a commit from `p2p-cop-agent`. It is historical lecturer-simulator tag `v1.11` at `7cf3fc9cf563768916effc1f58c36504dfbe6d36`. Current simulator `v3.0.0` is `960499fd5e8777b4929625f5d8fdcf2ab4677b54`. |
| Template config hash `9f2c...e1a4` | Absent from all four files. The generated config artifact contains `f6e2262d58b09ce4a514d90727e841502b7c21f3a906c64455bad00fe3c44e64`. |
| Mutual hash `d494...050f` | Absent from all four files. The generated log contains `a30dee430e5825979101c842c1a97b01becfe4603d6bf40b733608c18a3f9c1b`; the generated result contains `d3c2fdc674f3b4ac60c62eab729a083cb91f0cd224ad50d6cf974a775580e76c`. |
| Example Git commit | The generated final result records `"unknown"` for both sub-game commit values. The declaration contains repository URLs, but no actual student Cop commit. |
| Artifact schema versions | All four generated files use `1.1`; book Appendix B shows shared config `1.2`; simulator runtime config uses `1.3`; simulator private config uses `1.10`. No compatibility policy follows from those labels. |

The exact file-byte hashes remain recorded in
[JSON_ARTIFACT_SCHEMAS.md](JSON_ARTIFACT_SCHEMAS.md). None equals a semantic
`config_sha256` or mutual-agreement hash; those hashes have different input scopes.

## Concepts that must remain separate

| Concept | Purpose | Current status |
|---|---|---|
| Match declaration artifact | Static series identity, repositories, endpoints, hardware, model, budget, and signatures | Book-backed artifact family; not a repository parity manifest |
| `config_sha256` | Locks the agreed shared match terms under an accepted byte/semantic algorithm | Required in principle; exact final profile still needs coordinator acceptance |
| Parity manifest | Lists every Cop-owned controlled repository path and its exact file hash | Coordinator architecture requirement for safe byte-for-byte Thief consumption |
| Manifest self-hash | SHA-256 of the parity manifest's own exact bytes, calculated separately | Required by the coordinator handoff; not interchangeable with `config_sha256` |
| Simulator `REQUIRED_TERMS` | Nine semantic term names checked for non-`None` values | Simulator-only runtime list; not a controlled repository path list |
| `validate_agreement` | Fails when one of those required semantic terms is missing | Necessary simulator preflight only; it neither performs the peer signature exchange nor proves repository parity |
| Simulator negotiation | Compares the two semantic term dictionaries and verifies a nonce-bound signature | Simulator implementation evidence; separate from `validate_agreement` |

## Claim classification

| Claim | Classification | Treatment |
|---|---|---|
| Exactly four artifact families and the documented filenames | `CONFIRMED` | Keep `AF-021` and `AR-001` |
| Six sub-games | `CONFIRMED` | Keep `AF-018` |
| Step-0 includes hardware/model/team/sub-game and exact played Git commit | `CONFIRMED` | Record the book requirement; the simulator's sealed record carries code version, not the required actual Git commit |
| Sorted compact unescaped-Unicode UTF-8 JSON | `SIMULATOR IMPLEMENTED / PROPOSED PROFILE` | Current simulator uses it; the book directly confirms only part of the complete cross-language profile |
| Odd/even role alternation | `SIMULATOR IMPLEMENTED / NOT BOOK-CONFIRMED` | Do not make it binding until coordinator acceptance or authenticated lecturer evidence |
| `1.3` shared, `1.1` artifacts, and `1.10` private are one accepted compatibility policy | `NOT CONFIRMED` | These are different simulator labels, not an accepted migration rule |
| Declaration replaces the parity manifest | `REJECTED` | Match artifacts and repository handoff integrity solve different problems |
| `config_sha256` replaces controlled per-file hashes | `REJECTED` | It cannot prove exact parity of schemas, policy documents, fixtures, and checker code |
| Passing `validate_agreement` alone opens gameplay | `REJECTED` | The simulator performs later peer negotiation; this project additionally requires an accepted handoff, parity, conformance, and final coordinator freeze |

## Current Cop evidence

Coordinator review of immutable Cop candidate
`b586af9e55dcc40789a1d7ab683edb97c8cfabc6` concluded:

- local health: pass;
- provisional Thief copy: not authorized;
- final freeze: no-go;
- gameplay: no-go;
- portability remediation: authorized.

`665bd30a75866e872f899eb337664266e26129ed` was previously described as a local-only
head. It has since been pushed to the `agent/cop-m1-contract-revision` remote branch
and is now remotely available. Two further commits followed it: `459cd73` (reduced
the controlled set from 20 to 18 paths by moving `config/rate_limits.json` and
`docs/schemas/rate-limits.schema.json` to the local tier) and `e0df5ba` (updated
documentation to mark the candidate ready for external review). The branch was
subsequently merged to Cop main at
`be705f9dc9e14b9fc8a53ffe1658493ad977f1fc` via PR #8 (2026-07-28).

The latest remotely available Cop candidate is
`e0df5ba530fd7c433d41a98c5976ca7e08cdfa53`. Its handoff document labels the bundle
`0.1.0-proposed`, `UNFROZEN`, and `NO-GO UNTIL PARITY`, and states explicitly "This
handoff is for coordinator review." It records 18 controlled paths, a proposed
manifest exact-byte SHA-256 of
`473982dc01594b1c7abee8fc7f20cf665a6b245e53114ed4a2732c115a35d86a`, and a proposed
canonical config vector of
`adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db`.

The candidate self-reports the following proposed controlled paths and SHA-256 values:

| Proposed controlled path | Proposed SHA-256 |
|---|---|
| `.gitattributes` | `f9eaec26456d492ccc58aec75ce3a8e6e7680fb158b23da3977bcfa02b22c1ba` |
| `config/game.json` | `70758af55f178a049a438b81eb5f9acd389c568214cb3006358c66f8d10abd06` |
| `docs/contracts/ARTIFACT_CONTRACT.md` | `33d218b9d071ae40b7cd90f802c75a170cb30e9fd0c43eb61c2622140f034337` |
| `docs/contracts/CONTRACT_VERSION` | `9e061d4d08ca911d12915da01033a8a9f03cd0329a6ba33bbb953d6bba9edbda` |
| `docs/contracts/LEAGUE_CONTRACT.md` | `fac906032ac8a7138b177d2512940d84692ebec23f5377b8c0ccc0bb53b9af78` |
| `docs/contracts/MATCH_CONFIGURATION.md` | `e476ebafeed0d66522a7d96535d43dfc7f598413b0b1553d6d5e8c973afd2f23` |
| `docs/contracts/PRIVATE_CONFIGURATION.md` | `16b13bc8e8dd3cf17234a27e36623970153961d322b4895d3be9241931eeb745` |
| `docs/contracts/SHARED_RULES.md` | `ce080c2edc9b9965f0b2601144a425d22a25623f305af1a16a7c9aa39733a643` |
| `docs/schemas/artifact-keyset-fixture.schema.json` | `8e56b199fb6339a1d085422face33fac8313efd8b7d0d142774607b2febd7a3f` |
| `docs/schemas/config-hash-vector.schema.json` | `6477d028ac010cd5ae288f6d469ba8ca89055fe7681f8937fbcedc52f3878d86` |
| `docs/schemas/game-config.schema.json` | `fda84cf295788fda09e93e0e56d8876ae549ff7f1e99391d03552e86f04860d9` |
| `scripts/check_shared_contracts.py` | `b29bd3c978baf7b1b988e7a37c644cdc3b3e5fb548e852e0238fa95bac855b39` |
| `scripts/shared_contract_integrity.py` | `3f9dc0eb48a8ca9c5de83a287ffffb88bcc27aec7aeb6e64fe59140e6591b78b` |
| `tests/fixtures/contracts/agreed_config.keyset.json` | `a82c0f98a9eccb35d13dffb5287f1c74f65918008de4c178c3565540cb1ec1bf` |
| `tests/fixtures/contracts/declaration.keyset.json` | `fa80c357f5b9b1266ca8b22f9a588d7644735ef948ff26744e0e1b4e0232eeb4` |
| `tests/fixtures/contracts/final_result.keyset.json` | `032da7375bb220a298858d89d214a8504946cfa783e815940474bd354deec479` |
| `tests/fixtures/contracts/game-config-sha256.vector.json` | `116f790324b0bdfd28cc38926c2667ae6c9feabaea7b4e2e74662e5fc8dbea54` |
| `tests/fixtures/contracts/game_log.keyset.json` | `d084554908c831f7924b8ce943470443f3ee82ef829e8f0b2b44dc0017c3639b` |

These are proposed candidate values self-reported by the Cop. They are not accepted
handoff values. No coordinator verdict supplies `ACCEPTED_FOR_PROVISIONAL_PARITY: YES`
tied to these values. All Stage A items in `CONTRACT_HANDOFF_CHECKLIST.md` remain
MISSING. The Thief has not copied and must not copy any shared file.

## What is required next

1. Coordinator reviews an immutable, remotely available remediated Cop commit.
2. Coordinator explicitly authorizes that exact candidate for provisional
   parity/conformance testing and supplies its manifest hash, ordered paths, and
   per-file hashes.
3. Thief verifies the handoff before copying any byte.
4. Thief copies every controlled path exactly and proves local integrity,
   cross-repository parity, and bidirectional neutral-opponent conformance.
5. Remaining external schema/provenance/identifier decisions are resolved.
6. Coordinator issues a separate final contract-freeze verdict.
7. Only then may M2 gameplay begin.
