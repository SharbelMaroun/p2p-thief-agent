# Specification Conflicts and Unresolved Discrepancies

| ID | Issue | Status | Impact | Resolution evidence |
|---|---|---|---|---|
| C-001 | Historical draft `num_games = 1` is superseded by the fixed value of 6 sub-games per series. | `CONFIRMED` | Series/config/scoring | Official project book v3.0.0, Appendix F, Table 18, page 138 |
| C-002 | README described as five content components plus a cross-link conflicts with “six mandatory sections.” | `CONFLICT` | Academic report | Exact Chapter 9.4.2 and Appendix C text |
| C-003 | Simulator tool names appear as `submit_audit`, `exchange_audit`, or another name. | `UNKNOWN` | MCP contract | Centralized verified simulator reverse-engineering export |
| C-004 | `rmisegal@gmail.com` is for general contact/repository sharing; `rmisegal+uoh26finalgame@gmail.com` is for automated JSON reports. | `CONFIRMED` | Reporting | Official project book v3.0.0, Appendix F, Table 20, page 141 |
| C-005 | Previous references pointed to Appendix G for GitHub submission requirements; book v3.0.0 uses Appendix C. | `CONFIRMED` | Documentation citations | Corrected to Appendix C |
| C-006 | Whether all four reporting artifacts must be byte-identical is unresolved. | `UNKNOWN` | Reporting/contracts | Official JSON templates and direct book text |
| C-007 | Whether a stateless common package is allowed is unresolved; shared live state is separately prohibited by `SR-004`. | `UNKNOWN` | Shared architecture | Official rule or lecturer clarification |

No unresolved entry is resolved by selecting an example or simulator default.
