# Contract Consumption Handoff Checklist

Status: **BLOCKED — NO ACCEPTED HANDOFF**

This checklist is fail-closed. Candidate
`84339c210c8e3293d972bccec5912abf519d502c` is unfrozen and
coordinator-rejected; it is not an accepted value for any field below.

## Required handoff values

| Required value | Current state | Acceptance rule |
|---|---|---|
| `ACCEPTED_COP_COMMIT` | MISSING | Full immutable Cop commit SHA supplied by the coordinator |
| `ACCEPTED_CONTRACT_VERSION` | MISSING | Exact accepted/frozen public-contract version |
| `ACCEPTED_MANIFEST_SHA256` | MISSING | 64-hex SHA-256 of the manifest's exact bytes |
| `ACCEPTED_CONTROLLED_PATHS` | MISSING | Complete ordered path list from the accepted manifest |
| Per-file hashes | MISSING | One accepted 64-hex SHA-256 for every controlled path |
| Coordinator acceptance verdict | REJECTED / NO ACCEPTED VERDICT | Explicit acceptance of the exact commit, version, manifest hash, paths, and file hashes |

If any value is missing, ambiguous, internally inconsistent, or attached to a different
commit, stop. Do not copy or generate shared files.

## Pre-copy verification

- [ ] Record all six required handoff inputs without abbreviating hashes.
- [ ] Read the candidate only from `ACCEPTED_COP_COMMIT`, never from the Cop working tree.
- [ ] Verify the coordinator verdict names the same commit and contract version.
- [ ] Hash the manifest's exact bytes and compare with `ACCEPTED_MANIFEST_SHA256`.
- [ ] Confirm the manifest contract version equals `ACCEPTED_CONTRACT_VERSION`.
- [ ] Confirm the manifest path list exactly equals `ACCEPTED_CONTROLLED_PATHS`.
- [ ] Confirm there is exactly one accepted per-file hash for every controlled path.
- [ ] Independently review source claims and confirm no simulator-only behavior is mandatory.
- [ ] Confirm stable league, negotiated per-match, and private peer boundaries are explicit.
- [ ] Confirm neutral-opponent participant/match binding and canonicalization are resolved.

## Exact-byte consumption

- [ ] Copy every accepted controlled path directly from `ACCEPTED_COP_COMMIT`.
- [ ] Do not edit, reformat, rename, regenerate, or partially select a controlled file.
- [ ] Do not add a Thief-authored shared field or competing schema.
- [ ] Recompute every copied file's SHA-256 and compare it with the accepted per-file hash.
- [ ] Recompute the manifest self-hash separately.
- [ ] Confirm the controlled path set has no missing or unexpected entries.
- [ ] Confirm Thief has no runtime import, mount, or filesystem dependency on Cop.

## Conformance and freeze evidence

- [ ] Thief accepts a neutral compliant opponent's byte-identical match configuration.
- [ ] Thief creates a match configuration the neutral opponent accepts.
- [ ] Participant mutation, negotiated-value mutation, unsupported version, hash mismatch,
      ordering violation, and shared/private leakage fail before gameplay.
- [ ] Thief quality and contract gates pass.
- [ ] Cop quality and contract gates pass independently.
- [ ] Cross-repository per-file hashes and manifest self-hash match.
- [ ] Coordinator issues the final freeze/acceptance verdict for the verified result.

Only after every box is satisfied may M1 be marked complete. M2 remains blocked until
that point.
