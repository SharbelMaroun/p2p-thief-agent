# Contract Consumption Handoff Checklist

Status: **BLOCKED — NO PROVISIONAL COPY AUTHORIZATION**

This checklist is fail-closed and separates two coordinator decisions:

1. provisional authorization to copy an unfrozen candidate for parity and
   conformance testing;
2. final contract freeze after those tests and remaining external decisions pass.

This avoids the circular requirement that Thief parity exist before copying while
also requiring final freeze before copying. No candidate has provisional copy
authorization: original `84339c2`, revised `b586af9`, and the latest `e0df5ba`
(Cop main `be705f9`) were all rejected. The `e0df5ba` rejection is the explicit dated
coordinator verdict `ACCEPTED_FOR_PROVISIONAL_PARITY: NO` of 2026-07-28 — hashes are
integrity-correct but the contract is semantically rejected across seven issues. See
[COORDINATOR_VERDICT_2026-07-28.md](COORDINATOR_VERDICT_2026-07-28.md).

## Stage A — required provisional handoff values

| Required value | Current state | Provisional acceptance rule |
|---|---|---|
| `PROVISIONAL_COP_COMMIT` | MISSING | Full immutable, remotely available Cop commit SHA named by the coordinator |
| `PROVISIONAL_CONTRACT_VERSION` | MISSING | Exact candidate version; it may remain explicitly proposed/unfrozen |
| `PROVISIONAL_MANIFEST_SHA256` | MISSING | Coordinator-supplied 64-hex SHA-256 of the manifest's exact bytes |
| `PROVISIONAL_CONTROLLED_PATHS` | MISSING | Complete ordered path list from that exact manifest |
| Provisional per-file hashes | MISSING | One coordinator-supplied 64-hex SHA-256 for every controlled path |
| Coordinator provisional verdict | EXPLICIT NO (2026-07-28) | Explicit `ACCEPTED_FOR_PROVISIONAL_PARITY: YES` for the same commit and metadata; the coordinator issued `NO` for `e0df5ba`/`be705f9` |

If any value is missing, ambiguous, internally inconsistent, or attached to a different
commit, stop. Do not copy or generate shared files.

## Pre-copy verification

- [ ] Record all six provisional handoff inputs without abbreviating hashes.
- [ ] Read the candidate only from `PROVISIONAL_COP_COMMIT`, never from the Cop working tree.
- [ ] Verify the coordinator verdict names the same commit and contract version.
- [ ] Hash the manifest's exact bytes and compare with `PROVISIONAL_MANIFEST_SHA256`.
- [ ] Confirm the manifest contract version equals `PROVISIONAL_CONTRACT_VERSION`.
- [ ] Confirm the manifest path list exactly equals `PROVISIONAL_CONTROLLED_PATHS`.
- [ ] Confirm there is exactly one provisional per-file hash for every controlled path.
- [ ] Independently review source claims and confirm no simulator-only behavior is mandatory.
- [ ] Confirm stable league, negotiated per-match, and private peer boundaries are explicit.
- [ ] Confirm runtime match instances can vary without editing stable controlled files.
- [ ] Confirm every controlled script and policy is role-neutral in copied operation.

## Exact-byte consumption

- [ ] Copy every provisionally accepted controlled path directly from
      `PROVISIONAL_COP_COMMIT`.
- [ ] Do not edit, reformat, rename, regenerate, or partially select a controlled file.
- [ ] Do not add a Thief-authored shared field or competing schema.
- [ ] Recompute every copied file's SHA-256 and compare it with the provisional
      per-file hash.
- [ ] Recompute the manifest self-hash separately.
- [ ] Confirm the controlled path set has no missing or unexpected entries.
- [ ] Confirm Thief has no runtime import, mount, or filesystem dependency on Cop.

## Stage B — parity and conformance evidence

- [ ] Thief accepts a neutral compliant opponent's byte-identical match configuration.
- [ ] Thief creates a match configuration the neutral opponent accepts.
- [ ] Two different valid participant/match pairs work without changing any controlled
      stable-contract byte.
- [ ] Participant mutation, negotiated-value mutation, unsupported version, hash mismatch,
      ordering violation, and shared/private leakage fail before gameplay.
- [ ] Thief quality and contract gates pass.
- [ ] Cop quality and contract gates pass independently.
- [ ] Cross-repository per-file hashes and manifest self-hash match.

## Stage C — final freeze

- [ ] Authenticated-source and formal-schema blockers required by the coordinator are
      resolved or explicitly accepted as project-level interoperability decisions.
- [ ] Coordinator reviews the parity/conformance evidence.
- [ ] Coordinator supplies the final accepted contract version and exact freeze
      revision.
- [ ] Coordinator issues `CONTRACT_FREEZE: GO`.
- [ ] Coordinator separately issues `M2_GAMEPLAY: GO`.

Provisional copy permission authorizes only M1 parity/conformance work. Only after
every Stage A–C box is satisfied may M1 be marked complete or gameplay begin.
