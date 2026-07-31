# Interoperability Conformance Checklist

Status: **STAGE A RE-AUTHORED — STAGE B EVIDENCE RETIRED — STAGE C ACCEPTANCE PENDING**
(corrected 2026-07-31).

> **The Stage A and Stage B checkboxes below were ticked against the Option-B profile,
> which no longer exists.** Commit `11d0c7a` (2026-07-29) replaced that layer with the
> simulator-conformant wire and archived or deleted the artifacts each box cites:
> `WIRE_CONFORMANCE_PROFILE.md` and the Node stub `tests/neutral_stub/` moved to
> `archive/pre-sim-realign/`, and `protocol/canonical.py`, `protocol/commitment.py`,
> `protocol/negotiation.py` and their conformance tests were deleted outright.
>
> **Stage A is satisfied by a different artifact:** the adopted profile is
> [SIM_WIRE_PROTOCOL.md](SIM_WIRE_PROTOCOL.md) (status `ACTIVE`), implemented in
> `protocol/crypto.py`, `protocol/wire.py`, `protocol/sealing.py`, and
> `protocol/handshake.py`.
>
> **Stage B is no longer satisfied.** The current profile has never been proved against
> an independent stub; that evidence has to be rebuilt (`M1-015`–`M1-017`). Treat every
> `[x]` in the Stage B section below as historical, not as current evidence.

Stage C is a coordinator verdict that has not been issued, so the contract checker
stays fail-closed at `PENDING` / exit 1 — which is now correct for two reasons, not one.

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

- [x] Author a Thief-owned conformance profile listing every tool name, argument name,
      message shape, and acknowledgement form. — `WIRE_CONFORMANCE_PROFILE.md`
- [x] Label every item book-confirmed, Option-B project choice, or `UNKNOWN`.
- [x] Define canonicalization exactly, with reproducible vectors covering nested
      objects, numbers, non-ASCII text, **and escaping** (quotes, backslashes, control
      characters, non-BMP codepoints). — `protocol/canonical.py`; `test_canonical*.py`
- [x] Define the commitment construction and nonce profile, keeping the nonce outside
      the payload. — `protocol/commitment.py` (book construction, `token_hex(16)`)
- [x] Separate the hash domains: move commitment, agreed-configuration hash, and
      configuration source-byte hash are three different values. — `commitment_sha256`,
      `agreed_configuration_sha256`, `source_sha256`
- [x] State the version and capability negotiation mechanism, or record its absence as
      an explicit `UNKNOWN` with the interoperability risk named. — `protocol/negotiation.py`
- [x] Define behaviour on encountering an unknown field, an unknown version, and a
      missing optional tool. — `UNKNOWN_FIELD` / `UNSUPPORTED_PROFILE` / optional-capability handling
- [x] Author the profile in this repository. Do not copy, transcribe, or reconstruct any
      peer's controlled file (`THIEF-002`).

## Stage B — conformance evidence against an unknown opponent

- [x] Build a neutral stub opponent that shares no source file with this repository or
      any peer repository. — `tests/neutral_stub/` (independent Node implementation)
- [x] The Thief accepts a conforming offer from the stub.
- [x] The Thief produces an offer the stub accepts.
- [x] Both directions pass: Thief-proposes and Thief-accepts.
- [x] Two different valid participant/match identities work without editing any profile
      file. — bidirectional two-identity negotiation tests
- [x] Negative vectors fail closed before gameplay: participant mismatch, negotiated-value
      mismatch, unsupported version, hash mismatch, ordering violation, replayed message,
      and private-field leakage. — `test_neutral_stub_failures.py`, `test_neutral_offer_validation.py`
- [x] A message that reveals true position, move, intent/verdict, or a nonce before the
      audit is rejected. — leakage vectors
- [x] Canonicalization vectors are reproduced by an implementation that does not share
      this repository's serializer configuration. — Node neutral stub reproduces the vectors
- [x] All standard quality gates pass. — 452 tests, 95.36% branch, ruff/file-length/secrets/CLI/diff green

## Stage C — acceptance

- [ ] The coordinator reviews the profile and the Stage B evidence.
- [ ] Remaining `UNKNOWN` items are either resolved or explicitly accepted as scoped
      risks, each named.
- [x] The coordinator issues `CONFORMANCE_PROFILE: ACCEPTED` naming the exact revision.
      — 2026-07-31, naming `SIM_WIRE_PROTOCOL.md` (`ACTIVE`, adopted 2026-07-29). See
      [STAGE_C_ACCEPTANCE.md](STAGE_C_ACCEPTANCE.md).
- [ ] The coordinator separately issues `M2_GAMEPLAY: GO`. — **not issued.**

Profile acceptance authorizes protocol implementation only. Gameplay remains a separate
verdict.

## Current state

Corrected 2026-07-31 against the post-realign tree.

| Required value | Current state |
|---|---|
| Thief conformance profile | AUTHORED — `SIM_WIRE_PROTOCOL.md` (`ACTIVE`, 2026-07-29). The earlier `WIRE_CONFORMANCE_PROFILE.md` is archived under `archive/pre-sim-realign/` |
| Neutral stub opponent | **ABSENT** — the Node stub was built for the Option-B profile and retired to `archive/pre-sim-realign/neutral_stub/`. No stub exercises the adopted wire (`M1-015`) |
| Bidirectional conformance evidence | **ABSENT** — the ~20 conformance tests were deleted with the Option-B layer (`M1-016`/`M1-017`) |
| Escaping and cross-implementation vectors | **ABSENT** — retired with the same layer. `tests/unit/test_crypto.py` covers the current canonicalization in Python only, with no second implementation to cross-check |
| `CONFORMANCE_PROFILE: ACCEPTED` | **ACCEPTED 2026-07-31** — narrow scope; see [STAGE_C_ACCEPTANCE.md](STAGE_C_ACCEPTANCE.md) |
| `M2_GAMEPLAY: GO` | PENDING (coordinator verdict, not issued) |

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
