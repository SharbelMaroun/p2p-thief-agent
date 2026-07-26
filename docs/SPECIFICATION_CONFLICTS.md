# Specification Conflicts and Decisions

| ID | Issue | Status | Controlling treatment | Evidence / ADR |
|---|---|---|---|---|
| C-001 | One-game example/default versus six sub-games per official series | `RESOLVED` | Use fixed six; one-game values are examples only | Appendix F Table 18; `AF-018` |
| C-002 | “Five README components plus cross-link” versus “six components” | `RESOLVED` | Cross-link is component six | Chapter 9.4.2; Appendix E rule 42; `SR-008` |
| C-003 | Simulator tool names vary or are absent from the book | `OPEN` | Treat simulator names as candidates only | ADR-0001; `U-003` |
| C-004 | `rimesegal` aliases versus official `rmisegal` addresses | `RESOLVED` | Use only `rmisegal@gmail.com` and `rmisegal+uoh26finalgame@gmail.com` | Appendix F Table 20; `AF-020` |
| C-005 | Archived references cite Appendix G for GitHub submission | `RESOLVED` | Current book v3.0.0 uses Appendix C | Official book Appendix C |
| C-006 | Claim that all four artifacts must be byte-identical | `RESOLVED` | Shared game config must be byte-identical; no evidence makes all role-specific artifacts identical | Appendix E rule 11; `AE-011`; `JS-002/003` |
| C-007 | Shared live state prohibition versus possible shared executable package | `OPEN` | No runtime dependency; use independent accepted file copies in M1 | `SR-004`; `U-010` |
| C-008 | Appendix B `schema_version` example `1.2` versus unauthenticated generated examples `1.1` | `OPEN` | Record both; do not normalize or freeze a supported version yet | PDF p.129; example hashes; ADR-0003 |
| C-009 | Book multiplicative scent decay versus simulator subtractive/immediate decay | `RESOLVED` | Book formula controls; simulator behavior must not be copied | Chapter 4.3, PDF p.43; pinned simulator export; ADR-0005 |
| C-010 | Branch claims LLM movement is categorically forbidden | `RESOLVED` | Deterministic movement is policy/default; rule 25 is a recommendation without automatic sanction | Appendix E rule 25; `AE-025`; ADR-0007 |
| C-011 | Documents claim Cop/Thief files are already byte-identical | `RESOLVED` | Make no parity claim until actual manifest comparison passes | Contract policy; `U-020` |
| C-012 | Generated template prose says roles switch, while the book confirms six sub-games but does not define an alternating schedule | `OPEN` | Do not enforce alternation or choose the starting role without binding evidence or joint acceptance | `AF-018`; `U-021`; local generated examples |
| C-013 | Appendix B links sorted-key canonical JSON to `config_sha256`, while Chapter 5 gives compact UTF-8 bytes only for a core commitment example | `OPEN` | Keep the confirmed primitives, but do not invent hash scope, self-field exclusion, or full JSON canonicalization rules | `CR-001`; `U-002`; ADR-0006 |

No open conflict is resolved by selecting a simulator default, populated example, or
unaccepted proposal.
