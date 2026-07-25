# ADR-0005: Scent Model

Status: Pending

## Evidence

Official project book v3.0.0 section 4.3 describes multiplicative decay; Appendix F
Table 16 fixes center intensity 0.9, decay 0.10, and a 5x5 window (`AF-016`). The
lecturer simulator's subtractive behavior has lower authority and is not adopted.

## Decision needed

The book's multiplicative equation controls. Emission shape, update order, turn
synchronization, bounds beyond the stated formula, and shared representation still
require cross-team acceptance. Simulator reuse remains rejected pending the
license/provenance review in ADR-0008. No scent behavior is authorized here.
