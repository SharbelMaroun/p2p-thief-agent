# Stage C — Conformance Profile Acceptance

Status: **ACCEPTED.** Confirmed by the coordinator on 2026-07-31.

Coordinator: Sharbel Maroun (repository owner)
Prepared and confirmed: 2026-07-31

Reversible: if the first live game contradicts the profile, revert this status to
`PENDING` and re-open `M4`. Nothing downstream is destroyed by doing so.

## Verdict

```text
CONFORMANCE_PROFILE: ACCEPTED
Revision:            SIM_WIRE_PROTOCOL.md, status ACTIVE, adopted 2026-07-29
Scope:               commit-reveal construction, canonical JSON, and the four-tool
                     surface, as the profile this repository implements against.
M2_GAMEPLAY:         NOT ISSUED (separate verdict, deliberately withheld)
```

Accepting the profile authorizes protocol and runtime implementation. It does **not**
declare interoperability proven, and it does **not** open gameplay.

## Why this is acceptable now

The blocker was that a profile could be self-consistent and still wrong, because Cop and
Thief are both Python and were written from the same reading. Independent evidence now
exists for the part that decides whether a match scores at all:

- `tests/unit/test_reference_vector.py` reproduces
  `78a31c516536350bfdb8a3ee4ba3e131ae0676d7b4b95d02ff94b1aa84b85e65`, a commit hash
  emitted by the **reference simulator** during a real match (`records[0]` of its own
  `docs/sample-run/log_segal-police-team-vs-segal-thief-team_g01.json`). That is a
  foreign implementation, not a vector this project authored.
- The same vector pins float rendering (`31.8`, `6.0`), the cross-language hazard a
  Python-only test cannot surface.
- The book's Chapter 5.3 construction yields a **different** digest on that record,
  confirming the divergence recorded in `C-013` is the interoperable choice rather than
  a deviation.

Under Appendix E rule 19 an audit mismatch is an automatic zero, so the commitment
domain was the highest-risk item. It is now evidenced.

## What is explicitly NOT accepted

This acceptance is narrow. The following stay open and must not be read as covered:

| Item | Status |
|---|---|
| Tool surface proven against an independent opponent | **OPEN** — `M1-015`–`M1-017` |
| `negotiate` message shape proven bidirectionally | **OPEN** |
| `ensure_ascii=False` pinned by a vector | **OPEN** — every reference record is pure ASCII, so no vector discriminates it; the setting rests on reading the simulator source |
| The three longer move records reproduced | **OPEN** — needs the raw log file, not a relayed quote |
| Gameplay authorization | **NOT ISSUED** |

The first localhost game (`M5-010`) is the natural test for the tool surface. Building a
stub opponent before building the real peer is not required by this acceptance.

## The contract checker stays red

`scripts/check_shared_contracts.py` returns exit 1 with `PENDING` unconditionally and is
**not** to be edited to pass. Its message still describes the withdrawn copy model
("no Cop-owned shared-contract proposal"), which no longer matches how M1 works.

Rewriting it to verify the accepted conformance profile instead is follow-up work, not
part of this acceptance. Until that happens the red checker is expected and correct —
it is the tool that is out of date, not the repository.

## Effect

On confirmation, `M4` may be completed and `M5` may begin. `M1-015`–`M1-017` remain
open work items.
