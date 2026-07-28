# Interoperability Conformance Checklist

Status: **IN PROGRESS — STAGE A PROFILE DEFINITION**

## Why this document changed on 2026-07-28

This file previously specified a **copy model**: receive Stage A values naming an
immutable Cop commit, copy that repository's controlled bytes verbatim, and prove
cross-repository byte parity. That model was superseded by team direction.

The reason is not procedural, it is evidential. League play is against classmates for
points, and `THIEF-002` now forbids any read or write access to the companion Cop
repository. **Byte-parity with one companion repository is evidence about that
repository and nothing else.** A classmate's agent has never seen those files, so
copying them proves nothing about whether the two peers can actually play. Proving
interoperability requires conformance to a stated profile, demonstrated against an
opponent that shares no files with either side.

The superseded copy model is retained in Git history. It must not be revived, and no
Cop-owned file may be copied under it.

## What replaces it

The Thief authors its **own** wire profile from the sources it is allowed to use, and
proves that profile against a neutral stub. Nothing is copied from any peer.

Authority for every profile item must be one of:

- **book-confirmed** — direct Appendix E/F or chapter evidence, cited exactly;
- **Option-B project choice** — a documented academic-freedom selection where the book
  leaves a wire detail open, per `OPTION_B_INTEROP_DECISION.md`;
- **`UNKNOWN`** — unresolved; keep the dependent choice `PENDING` and ask for an
  explicit decision before implementing it.

An item with no authority label is not part of the profile.

## Stage A — profile definition

- [ ] Author a Thief-owned conformance profile listing every tool name, argument name,
      message shape, and acknowledgement form.
- [ ] Label every item book-confirmed, Option-B project choice, or `UNKNOWN`.
- [ ] Define canonicalization exactly, with reproducible vectors covering nested
      objects, numbers, non-ASCII text, **and escaping** (quotes, backslashes, control
      characters, non-BMP codepoints).
- [ ] Define the commitment construction and nonce profile, keeping the nonce outside
      the payload.
- [ ] Separate the hash domains: move commitment, agreed-configuration hash, and
      configuration source-byte hash are three different values.
- [ ] State the version and capability negotiation mechanism, or record its absence as
      an explicit `UNKNOWN` with the interoperability risk named.
- [ ] Define behaviour on encountering an unknown field, an unknown version, and a
      missing optional tool.
- [ ] Author the profile in this repository. Do not copy, transcribe, or reconstruct any
      peer's controlled file (`THIEF-002`).

## Stage B — conformance evidence against an unknown opponent

- [ ] Build a neutral stub opponent that shares no source file with this repository or
      any peer repository.
- [ ] The Thief accepts a conforming offer from the stub.
- [ ] The Thief produces an offer the stub accepts.
- [ ] Both directions pass: Thief-proposes and Thief-accepts.
- [ ] Two different valid participant/match identities work without editing any profile
      file.
- [ ] Negative vectors fail closed before gameplay: participant mismatch, negotiated-value
      mismatch, unsupported version, hash mismatch, ordering violation, replayed message,
      and private-field leakage.
- [ ] A message that reveals true position, move, intent/verdict, or a nonce before the
      audit is rejected.
- [ ] Canonicalization vectors are reproduced by an implementation that does not share
      this repository's serializer configuration.
- [ ] All standard quality gates pass.

## Stage C — acceptance

- [ ] The coordinator reviews the profile and the Stage B evidence.
- [ ] Remaining `UNKNOWN` items are either resolved or explicitly accepted as scoped
      risks, each named.
- [ ] The coordinator issues `CONFORMANCE_PROFILE: ACCEPTED` naming the exact revision.
- [ ] The coordinator separately issues `M2_GAMEPLAY: GO`.

Profile acceptance authorizes protocol implementation only. Gameplay remains a separate
verdict.

## Current state

| Required value | Current state |
|---|---|
| Thief conformance profile | IN PROGRESS |
| Neutral stub opponent | PENDING |
| Bidirectional conformance evidence | PENDING |
| Escaping and cross-implementation vectors | PENDING |
| `CONFORMANCE_PROFILE: ACCEPTED` | PENDING |
| `M2_GAMEPLAY: GO` | PENDING |

## Checker semantics

`scripts/check_shared_contracts.py` remains **fail-closed** at `PENDING` with exit 1 and
must never be edited to report a pass before Stage C completes. Its message still uses
the historical copy-model wording about a missing proposal or parity manifest. Under the
conformance model, read that `PENDING` as: **no accepted conformance profile exists.**
The exit code and the fail-closed guarantee are unchanged.

## What is explicitly no longer required

- Receiving an immutable peer commit SHA, manifest hash, controlled-path list, or
  per-file hashes.
- Copying any peer file byte-for-byte.
- Proving cross-repository byte parity.

None of these ever proved interoperability with an unknown opponent, which is the only
interoperability the league actually tests.
