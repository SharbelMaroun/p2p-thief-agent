# Simulator-Conformant Wire Protocol

Status: **ACTIVE** (adopted 2026-07-29). Supersedes the archived Option-B profile
(`archive/pre-sim-realign/`).

Authority: the reference simulator `Game-P2P-Cop-Chase` (rmisegal) **defines wire
serialization**; the project book governs concepts and rules. Everything here is
independently authored to match that wire for cross-agent league interoperability — no
simulator code is copied (it is EULA-licensed; we match field shapes only).

## Tools (each peer's own FastMCP server — live transport is M5)

| Tool | Argument | Purpose |
|---|---|---|
| `negotiate` | `message` | signed-terms agreement + `config_sha256` |
| `receive_turn` | `message` | opponent's `TurnMessage` (the turn token travels with it) |
| `submit_audit` | `payload` | end-of-game `AuditPayload` (records + nonces) |
| `receive_control` | `message` | opt-in control channel |

There is **no envelope** — the tool argument *is* the message dict.

## Commit-reveal (`protocol/crypto.py`)

```text
commit = SHA256(canonical_json(payload) + "|" + nonce)
canonical_json = json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":"))
nonce = secrets.token_hex(16)   # 32 lowercase hex
```

### Verified against real reference output — 2026-07-31

This is no longer an asserted reading. `tests/unit/test_reference_vector.py` reproduces
the commit hash
`78a31c516536350bfdb8a3ee4ba3e131ae0676d7b4b95d02ff94b1aa84b85e65` from
`records[0]` of the simulator's own
`docs/sample-run/log_segal-police-team-vs-segal-thief-team_g01.json` — real match output
from an implementation this project did not write. The vector also pins float rendering
(`ram_gb 31.8`, `vram_gb 6.0`), the classic cross-language canonicalization hazard that
a Python-only test cannot surface. The book's Chapter 5.3 construction (nonce inside,
no delimiter) yields a **different** digest on the same record, which is direct evidence
that following the book literally would fail every cross-peer audit.

Two limits are recorded honestly rather than glossed:

1. **`ensure_ascii=False` is not pinned by any vector.** Every record in the reference
   log is pure ASCII, so `True` and `False` produce identical bytes there. The setting
   rests on reading `ensure_ascii=False` in the simulator's own
   `src/police_thief/domain/crypto.py`. It becomes load-bearing the moment a hint
   carries a non-ASCII character — an accented New York landmark, a curly quote — so it
   must not be "simplified" later.
2. **Three longer move records did not reproduce.** Their payloads carry ~900-character
   `llm_prompt` strings containing newlines, escaped quotes, and literal `|`
   characters, relayed through a notebook UI rather than read from the raw file. The
   competing hypothesis — that the log stores more than it seals — was tested by
   brute-forcing every subset of the top-level keys and is **refuted**: no subset
   reproduces the recorded digest, and the simulator source states the logged `payload`
   is exactly the sealed object. Transcription loss is the remaining explanation, but
   it is not proven. Closing this needs the raw log file, not a relayed quote.

The committed payload roster observed for a move record is `step`, `state`, `position`,
`move`, `intent`, `verdict`, `hint`, `prompt_discussion` (`llm_prompt`,
`llm_reasoning`, `bluff_classification`), `model`, `tokens_step`, `tokens_total`,
`response_seconds`, `random_move` — the whole object is sealed, including reasoning and
timing.

Verification re-hashes the revealed payload **as received**, so the committed field
roster is each peer's own choice, never a cross-peer schema. The same `canonical_sha256`
hashes the agreed config and audits. Our sealed step payload roster lives in
`protocol/sealing.py` (`sealed_step_payload`).

## Messages (`protocol/wire.py`)

- **TurnMessage**: `step, sender, hint, smell_grid, commit, timestamp` (+ optional
  `barrier_placed, capture_claim, claim_response, win_claim`). `smell_grid` is a dict
  `{"r,c": intensity}`. Rejects unknown fields.
- **ControlMessage**: `kind, sender` (+ `sub_game_number, status, step_budget, payload`).
  Ignores unknown keys (matching the sim).
- **AuditPayload**: `sender, records[{payload,nonce,commit}], result_claim` where
  `result_claim ∈ {capture, survival, timeout}`. Rejects unknown fields.

## Handshake (`protocol/handshake.py`)

Each peer signs `commit_of(terms, nonce)` and verifies the opponent signed the **same**
terms. Identity is per-group and **carries no role** (roles alternate across sub-games);
it is exchanged but not signed. `config_sha256 = canonical_sha256(terms)`.

## Outcome / scoring

`state.scoring.wire_result_claim(Outcome)` maps the M3 outcome to the wire claim:
`CAPTURE→capture`, `SURVIVAL→survival`, `TECHNICAL_LOSS→timeout` (the sim's 0/0 bucket).
`TIE` is series-level only. Table-17 point values already match the simulator.

## Resolved unknowns (see `UNKNOWN_REQUIREMENTS.md`)

U-002 (canonicalization), U-003 (tool surface), U-004 (handshake), U-005 (commitment),
U-014 (event ordering), U-021 (role schedule: 1/3/5 natural, 2/4/6 swapped, Thief first)
are now settled by the lecturer's authoritative answer.
