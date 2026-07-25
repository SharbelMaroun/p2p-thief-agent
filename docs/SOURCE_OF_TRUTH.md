# Source of Truth

Status date: 2026-07-25.

Requirements are evaluated in this order:

1. Official assignment book `police_thief_p2p.pdf`, version 3.0.0, including
   Appendices E and F.
2. Official course JSON templates.
3. Lecturer simulator at exact commit
   `960499fd5e8777b4929625f5d8fdcf2ab4677b54`.
4. Dated lecturer or Moodle clarification.
5. Professional Software Submission Guidelines v3.0.
6. A cross-team ADR accepted by both peers.
7. Current repository documents.
8. Archived documents, NotebookLM text, translations, summaries, team notes, and AI
   plans.

The higher-ranked direct source controls. Appendix F is the book's controlling
quantitative table. Simulator behavior is an interoperability and learning reference,
not a submission skeleton, and cannot override the book.

Every evaluated claim uses exactly one status:

- `CONFIRMED`: direct authoritative evidence and exact location recorded;
- `CONFLICT`: authoritative evidence disagrees or a lower source conflicts with a
  higher source;
- `UNKNOWN`: direct evidence is absent, unreadable, ambiguous, or not pinned.

Only `CONFIRMED` ledger entries and accepted cross-team ADR decisions may guide
implementation. An ADR cannot override a higher-ranked official source.
