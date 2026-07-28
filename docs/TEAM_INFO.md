# Team Information

| Field | Status | Value / next evidence |
|---|---|---|
| Thief repository | `CONFIRMED` | <https://github.com/SharbelMaroun/p2p-thief-agent> |
| Cop companion repository | `CONFIRMED` | <https://github.com/SharbelMaroun/p2p-cop-agent> |
| General/repository-sharing address | `CONFIRMED` | `rmisegal@gmail.com` (`AF-020`) |
| Automated JSON-report address | `CONFIRMED` | `rmisegal+uoh26finalgame@gmail.com` (`AF-020`) |
| Team/group identifier | `CONFIRMED` | `sharNamr` — verified team input, 2026-07-28 (`U-016`) |
| Member names/identifiers | `CONFIRMED` | Amr safadi; Sharbel Maroun — verified team input, 2026-07-28 (`U-016`) |
| Eight-character team code | `CONFIRMED` | `sharNamr` — exactly 8 characters, no spaces, satisfies `SR-011`; verified team input, 2026-07-28 (`U-016`) |

Do not infer identity fields from Git authors, examples, translations, or archived
configuration. The values above were supplied directly by the team on 2026-07-28; that
direct input is their authority.

## Notes on these values

- The group identifier and the Moodle team code are deliberately the same string,
  `sharNamr`. They serve different purposes and are not required to match: the group
  identifier is exchanged publicly, while the team code is a submission field.
- `sharNamr` is therefore the value that will appear in `agreed_between` in a real
  shared `config/game.json` (`AB-002`). Both peers of this team use it, and it must be
  byte-identical on both sides of any match (`AE-011`).
- Because the identifier is reused as the code, the Moodle submission code will be
  visible to any opponent and in emitted artifacts. It is a grouping key rather than a
  credential, so this is recorded as a consequence, not a defect.
- Member names are recorded exactly as supplied, including capitalization.
