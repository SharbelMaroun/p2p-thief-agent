# `G008` — counted series vs `amireman`: why the filenames and the report disagree

**Read this before concluding that a linked artifact is missing.** Every file
`result_G008.json` points at exists. None of them is named what that report says.

This note was written on 2026-08-15, two days after the series was played and reported. It
changes nothing in the evidence; it explains it. The same file is in both repositories.

## What happened

This series was played on 2026-08-13, before `shared/series_identity.py` landed. At that
point the artifact writer derived its own identifier from the configuration digest —
`game-<12 hex of config_sha256>` — while the result report was already being built from the
`G00N` label the two teams had agreed. So the run produced **two internally consistent halves
that disagree with each other**:

| | `game_id` | `game_uid` |
|---|---|---|
| the six declaration/config/log artifacts | `game-772de8f029e4` | `772de8f029e42892faf7f4016f77c268` |
| `result_G008.json` (and the emailed report) | `G008` | `6aba9341-d92a-6e4b-a6a4-bb44ccadac1a` |

Appendix F table 20 names all four artifact families from `<game_id>`, and the book is
explicit that this identifier is the label the two teams agree — **not** a value derived from
a hash of the configuration, whose only job is locking that configuration under
`config_sha256`. The artifact half was wrong; the report half was right.

## The map from the report to the real files

`result_G008.json` declares its links as `log_G008_g<NN>.json`, `config_G008_g<NN>.json`,
`declaration_G008.json`. Substitute `game-772de8f029e4` for `G008` and you have the file. In
full, and noting which repository holds each — this side played Cop on the odd sub-games, so
the two halves of the series live in the two repositories:

| the report links | the actual file | repository |
|---|---|---|
| `declaration_G008.json` | `declaration_game-772de8f029e4.json` | both |
| `config_G008_g01.json` | `config_game-772de8f029e4_g01.json` | `p2p-cop-agent` |
| `config_G008_g02.json` | `config_game-772de8f029e4_g02.json` | `p2p-thief-agent` |
| `config_G008_g03.json` | `config_game-772de8f029e4_g03.json` | `p2p-cop-agent` |
| `config_G008_g04.json` | `config_game-772de8f029e4_g04.json` | `p2p-thief-agent` |
| `config_G008_g05.json` | `config_game-772de8f029e4_g05.json` | `p2p-cop-agent` |
| `config_G008_g06.json` | `config_game-772de8f029e4_g06.json` | `p2p-thief-agent` |
| `log_G008_g01.json` | `log_game-772de8f029e4_g01.json` | `p2p-cop-agent` |
| `log_G008_g02.json` | `log_game-772de8f029e4_g02.json` | `p2p-thief-agent` |
| `log_G008_g03.json` | `log_game-772de8f029e4_g03.json` | `p2p-cop-agent` |
| `log_G008_g04.json` | `log_game-772de8f029e4_g04.json` | `p2p-thief-agent` |
| `log_G008_g05.json` | `log_game-772de8f029e4_g05.json` | `p2p-cop-agent` |
| `log_G008_g06.json` | `log_game-772de8f029e4_g06.json` | `p2p-thief-agent` |
| `result_G008.json` | `result_G008.json` | `p2p-cop-agent` |

One link resolves the other way: the **declaration** lists
`result_game-772de8f029e4.json`, and the result artifact is the one file that was named under
the agreed scheme. Read it as `result_G008.json`.

## What was deliberately not done

**The artifacts were not renamed and their contents were not edited.** They are the record of
what actually ran, in a counted game, whose report has already been sent and whose outcome the
opponent has already agreed. Rewriting evidence after it is reported is indistinguishable from
rewriting evidence that was wrong, and the whole audit model here rests on records that nobody
touches after the fact. A mismatch that is explained costs a grader one paragraph; edited
evidence costs the reader their ability to trust any of it.

The mismatch is also cosmetic in the sense that matters most: `game_id` appears in **no commit
preimage**. The per-turn commitment covers `{step, state, move, position, barriers, intent,
verdict, hint}` and the nonce, so the identifier plays no part in any hash that an audit
recomputes. Nothing here is unverifiable because of it.

## Evidence that the series itself is sound

Re-verified 2026-08-15 with each repository's own `replay` command:

```
log_game-772de8f029e4_g01.json  Verified OK - 34 steps re-verified
log_game-772de8f029e4_g02.json  Verified OK - 35 steps re-verified
log_game-772de8f029e4_g03.json  Verified OK - 34 steps re-verified
log_game-772de8f029e4_g04.json  Verified OK - 35 steps re-verified
log_game-772de8f029e4_g05.json  Verified OK - 34 steps re-verified
log_game-772de8f029e4_g06.json  Verified OK - 35 steps re-verified
```

All six audits were exchanged and accepted at the time, both teams' reports agree on every
outcome-bearing field, and the series consensus digest
`95f4d5fc74fb49f5064afa438daeb1973916e20cc9a906d6ac519e148ab374db` was reproduced bit for bit
on both sides. Final score 47–47 (3–3 with Table 17 row 5's draw award of 2 per side).

## Where the defect was fixed

`shared/series_identity.py`, on 2026-08-13, after this series and after `G009` sub-game 1 hit
the same problem and that series was stopped and replayed from the start. `series_game_id`
now reads the agreed `G00N` label from the private configuration and **refuses** rather than
defaulting, and `derive_game_uid` derives the shared UUID from the agreed terms plus the
sorted group pair. `log_context` takes both as required keyword arguments.

`games/counted-uohay26-0813-G009/` is what a correct set looks like: every file named `G009`,
zero hash-derived names, and a result report whose links all resolve. `G008` predates the fix
and is the last set that does.
