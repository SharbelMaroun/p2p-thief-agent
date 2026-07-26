# Proposed Cryptographic and Configuration Gate Resolution Review

Review date: 2026-07-27

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

A later local-only Cop head was observed at
`665bd30a75866e872f899eb337664266e26129ed`. Its own handoff labels the bundle
`0.1.0-proposed`, `UNFROZEN`, and `NO-GO`. It records 20 controlled paths, manifest
exact-byte SHA-256
`ed09244a6b05a4832b8f4d85bc5881ae9eaea139023cd0e946b2bf994b32ad2d`,
and proposed config vector
`adac9efe6d51b9487c400a04c2e185af9fb3622e1a7d74f18d400425656d82db`.
Those are candidate evidence, not accepted handoff values. The commit was ahead of
its remote branch and had no coordinator acceptance verdict at review time.

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
