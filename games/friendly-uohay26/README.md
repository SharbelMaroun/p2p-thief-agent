# Friendly vs `uoh-ay26` — sub-game 1, 2026-08-11

Uncounted warm-up (`AE-52`). Nothing was emailed; reporting was structurally disabled.

## What the artifact says, and what actually happened

`log_game-5a7b4a6e58be_g01.json` records `survival` after 35 steps in the Thief role, and it
replays clean:

```
uv run p2p-thief replay --log games/friendly-uohay26/log_game-5a7b4a6e58be_g01.json
Verified OK — 35 steps re-verified
```

**The game nevertheless reconciles to 0/0 for both sides.** The opponent recorded a
`technical_loss`, because this peer wrote the log and exited the instant the horizon was
reached, and their `submit_audit` arrived a moment later at a live tunnel with no process
behind it:

    Opponent unreachable mid-match -- resolving as technical loss:
    submit_audit timed out: ... Server error '502 Bad Gateway'

Rule 35 scores conflicting reports 0 for both teams. Rule 36 makes the mutual audit a
condition of agreement, and an agreement needs two peers present. The fault was entirely
ours: their Cop behaved correctly throughout.

## `mutual_agreement.confirmed` in this file is wrong, and is left wrong on purpose

The artifact says `"confirmed": true`. **No mutual agreement took place.** At the time this
file was written the field was the literal `True` in `adapters/serve.py` — it had always meant
"negotiation succeeded", never "the result was agreed", and it was emitted unconditionally.

It is **not** edited here. A log is evidence, and quietly correcting a field to match what we
wish it had said is the behaviour rule 19 exists to punish; the honest record is the file as
it was produced, plus this note. Both defects are fixed in the code
(`adapters/post_match.py`), so no later artifact carries the same claim: `confirmed` is now
the return value of the audit wait.

## Provenance

| | |
|---|---|
| Opponent | `uoh-ay26` (Aisha Abu Dahesh, Yousef Asadi) |
| Their Cop | `https://cop.uohay26game.com/mcp` |
| Role | Thief (`sharNamr`) |
| Played | 2026-08-11 21:03:01 → 21:13:52 UTC |
| Config SHA-256 | `a1c7d39e8c21ee8ccf66c7e2dba99400cfd9a36c6e5c190d70ae487c8c8497b7` |
| Tokens | 0 (zero-token template provider) |
| Commit played | `6d586e60e0e1a41a9e0a0200a84c5310177efc4e` |

No `logs/wire.jsonl` accompanies this match: `services/wire_log.py` was written *because* of
this evening and did not exist while it was played.
