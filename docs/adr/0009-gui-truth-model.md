# ADR-0009: GUI Truth Model

Status: Proposed

## Evidence

Official project book v3.0.0 sections 2.2 and 7.3 define peer-local truth and a live GUI
that does not reveal objective world state. Chapter 2.4.2 separately forbids access to
the opponent's private truth (`SR-004`).

## Proposal awaiting acceptance

Limit the live GUI to Thief-local truth. Exact views, fields, refresh behavior, and the
separate replay truth model remain undecided; this placeholder implements no GUI.
