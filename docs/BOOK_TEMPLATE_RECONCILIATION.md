# Book and JSON Template Reconciliation

Audit date: 2026-07-27

This review compares official project book v3.0.0 with the four supplied local JSON
examples. The book is authoritative. The local files are preserved outside this
repository and are byte-identical to generated simulator artifacts previously found
on this machine, so their exact fields remain observational unless the book
independently confirms them.

## Classification

| Claim | Classification | Controlling conclusion |
|---|---|---|
| Every member submits separately in Moodle | `CONFIRMED` | Required by Chapter 11.5 and Appendix E |
| Team code is unique, eight characters, and has no spaces | `CONFIRMED` | Format is binding; the actual team value remains unknown |
| Use the Moodle Word template, do not change/move fields, export PDF | `CONFIRMED` | Preserve the official template exactly |
| Include a self-grade for code quality, not game outcome | `CONFIRMED` | Required in the Moodle report |
| Each peer sends its own agreed final JSON attachment through Gmail | `CONFIRMED` | Use `rmisegal+uoh26finalgame@gmail.com`; no free-text final report body |
| Both independently sent result files must be byte-identical | `PARTIAL` | Agreement and separate JSON delivery are binding; explicit byte identity is stated for shared game configuration, not both delivered result files |
| Final revision uses annotated tag `v1.0-submission` | `CONFIRMED` | Create only at final reviewed submission revision |
| Lecturer can access both repositories | `CONFIRMED` | Public or explicitly shared with `rmisegal@gmail.com` |
| README includes belief-map and Replay `Verified OK` screenshots | `CONFIRMED` | Required final submission evidence |
| `agreed_between` lists the two participating group IDs | `CONFIRMED` | Mandatory shared-config field; exact list order remains open |
| Shared `config/game.json` and private `config/game.toml` split | `CONFIRMED` | Shared values are signed/identical; private settings remain local; shared gameplay values override duplicates |
| Gmail API credentials belong in `config/game.toml` | `NOT CONFIRMED` | The book places email settings/target in private config but separately forbids tracked secrets; credential loading remains open |
| All four artifacts share `game_id`, `game_uid`, and `links` | `PARTIAL` | Common `game_uid` and filenames derived from `game_id` are confirmed; an exact mandatory `links` dictionary is not |
| `game_uid` must be a UUID and `game_id` must use the shown pattern | `NOT CONFIRMED` | These are example conventions until a binding schema or clarification exists |
| `config_sha256` uses sorted compact UTF-8 canonical JSON over the entire shared config | `PARTIAL` | Appendix B confirms sorted-key canonical JSON for consistent config hashing; Chapter 5 confirms sorted compact UTF-8 for the shown commit payload; exact config-hash scope and edge rules remain open |
| Six sub-games are required | `CONFIRMED` | Appendix F controls over populated one-game examples |
| Cop/Thief roles alternate in all six sub-games | `NOT CONFIRMED` | Generated template prose is insufficient; do not implement a schedule until accepted |
| Declaration/artifacts use 1.1 and shared configuration uses 1.2 compatibly | `UNRESOLVED` | Book config example is 1.2; generated examples are 1.1; no compatibility policy is stated |

## Evidence anchors

- Moodle/PDF rules: book PDF p.114 / printed p.98.
- Pre-submission runtime/reporting evidence: PDF p.113 / printed p.97.
- Shared JSON/private TOML and canonical-config discussion: PDF pp.126–130 /
  printed pp.110–114.
- Common artifact identity: PDF p.95 / printed p.79.
- Core commit serialization example: PDF p.53 / printed p.37.
- Repository, tag, and screenshot requirements: PDF pp.133–136 /
  printed pp.117–120.
- Automated reporting rules: PDF p.147 / printed p.131.
- Submission rules: PDF p.148 / printed p.132.
- Official addresses and filename patterns: Appendix F Table 20, PDF p.157 /
  printed p.141.

## Inspected local example hashes

- `1-pre-game-declaration.json`:
  `f0f54ada41b831fc666d18ba0605f656ec4ac21160a85653553bda8e574543e4`
- `2-agreed-config.json`:
  `4e7778d88bf53aa2d4dad0ad09c64764149d3ed0e521e578e77a3ab75773cba1`
- `3-game-log.json`:
  `00e783628585e85d9f7716faf337917090d5e4a5530d4bd10c239647002e71c2`
- `4-final-result.json`:
  `397bf9f00cf5aa4dfc609b6add10336d267056f8c2ef333e4b32a03a85d8d204`

## Implementation effect

This evidence narrows documentation and future validation work, but it does not
authorize gameplay implementation or modification of Cop-owned shared contract files.
M2 remains blocked until an accepted cross-repository contract handoff resolves
`U-020`, including the open schedule, canonicalization, schema-version, and formal
artifact-schema decisions.

Later supplied assertions about simulator `REQUIRED_TERMS`, odd/even `role_for()`,
schema labels, and fixed hash values are audited in
[GATE_RESOLUTION_REVIEW.md](GATE_RESOLUTION_REVIEW.md). They do not authenticate the
four files or replace the coordinator parity handoff.
