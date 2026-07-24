# Source of Truth

Status date: 2026-07-24.

Requirements are evaluated in this order:

1. official final-project book v3.0.0;
2. Appendix F for binding numerical values and modes;
3. Appendix E for mandatory rules;
4. official Moodle JSON templates;
5. newer official Moodle instructions and lecturer announcements;
6. Professional Software Submission Guidelines v3.0;
7. lecturer simulator at an explicitly recorded upstream commit;
8. project-book NotebookLM, for navigation only;
9. simulator-code NotebookLM, for navigation only;
10. translations, summaries, team notes, current repository documents, and AI plans.

The higher-ranked direct source controls. NotebookLM, summaries, translations, examples,
and simulator behavior do not independently establish a project requirement.

Every evaluated claim uses exactly one status:

- `CONFIRMED`: direct authoritative evidence and exact location recorded;
- `CONFLICT`: authoritative evidence disagrees or a lower source conflicts with a
  higher source;
- `UNKNOWN`: direct evidence is absent, unreadable, ambiguous, or not pinned.

Only `CONFIRMED` ledger entries may guide implementation.
