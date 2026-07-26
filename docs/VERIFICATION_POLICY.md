# Verification Policy

A requirement becomes `CONFIRMED` only when the reviewer records the authoritative
source, version, exact page/table/section or file/symbol, and a short faithful
paraphrase. Numerical values and modes require direct Appendix F evidence. Mandatory
rules require direct Appendix E evidence unless a higher-priority source controls.

Authenticated machine-readable official templates can confirm fields that are
present, ownership, identifiers, signatures, and filenames. Unauthenticated populated
examples prove only observations about their exact bytes; they do not prove
requiredness, optionality, types, enums, validation constraints, or official
provenance. Simulator
observations require its upstream URL and full upstream commit hash and remain
illustrative unless a higher source confirms them.

NotebookLM answers, translations, summaries, checklists, team plans, repository prose,
current configuration, and unconfirmed simulator behavior are insufficient alone.

Conflicts must be recorded without silently selecting a value. Before implementation:

1. update the source inventory and ledger;
2. resolve affected conflicts and unknowns;
3. obtain an accepted cross-team ADR for parity-controlled contracts;
4. copy accepted contract files byte-for-byte without a runtime repository dependency;
5. add tests traceable to confirmed requirements.

An unresolved item blocks only its dependent subsystem. It does not blanket-block
documentation, package scaffolding, or unrelated domain work. Newer Moodle or lecturer
instructions must be checked again before the affected release gate.
