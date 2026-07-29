# Lecturer Simulator Baseline

Status: pinned reference inspected through a verified planning export.

| Field | Value |
|---|---|
| Upstream | `https://github.com/rmisegal/Game-P2P-Cop-Chase.git` |
| Exact commit | `960499fd5e8777b4929625f5d8fdcf2ab4677b54` |
| Release subject | `Release v3.0.0 — align code and guidelines-book versions to 3.0.0` |
| Verified export | planning workspace `exports/simulator-shared/`, inspected 2026-07-24 |

The simulator is a learning and interoperability reference, not a submission skeleton.
Its implementation cannot override the book. In particular:

- do not copy its one-game demo/default into the official six-sub-game series;
- do not copy its subtractive/immediate scent decay; Chapter 4.3 is multiplicative;
- do not present `negotiate`, `receive_move`, `submit_audit`, or `receive_control` as
  mandatory book names;
- do not copy substantial source without an accepted license/provenance decision.

This M1 source tree was written as a clean behavior-free scaffold and contains no
lecturer simulator runtime code. ADR-0008 remains pending for any later reuse.
