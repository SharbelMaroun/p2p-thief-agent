# Source of Truth

Status date: 2026-07-26.

Requirements are evaluated in this order:

1. Official Final Project Book `police_thief_p2p.pdf`, version 3.0.0.
2. Appendix F mandatory parameters and statuses.
3. Appendix E mandatory rules.
4. Authenticated official JSON templates.
5. Current Moodle instructions and dated lecturer announcements.
6. Professional Software Submission Guidelines v3.0.
7. Lecturer simulator at exact commit
   `960499fd5e8777b4929625f5d8fdcf2ab4677b54`.
8. Lecture and assignment material.
9. Team notes, translations, repository prose, and previous AI reports.

The higher-ranked direct source controls. Appendix F is the book's controlling
quantitative table. The four locally observed JSON files are not authenticated
official templates: the coordinator found them byte-identical to generated simulator
logs, so their provenance remains `UNKNOWN`. Simulator behavior is an interoperability
and learning reference, not a submission skeleton, and cannot override the sources
above it.

Every evaluated claim uses exactly one status:

- `CONFIRMED`: direct authoritative evidence and exact location recorded;
- `CONFLICT`: authoritative evidence disagrees or a lower source conflicts with a
  higher source;
- `UNKNOWN`: direct evidence is absent, unreadable, ambiguous, or not pinned.

Only `CONFIRMED` ledger entries and accepted cross-team ADR decisions may guide
implementation. An ADR cannot override a higher-ranked official source.
