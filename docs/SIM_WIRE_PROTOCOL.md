# Simulator-Conformant Wire Protocol

Status: **ACTIVE** (adopted 2026-07-29). Supersedes the archived Option-B profile
(`archive/pre-sim-realign/`).

Authority: the reference simulator `Game-P2P-Cop-Chase` (rmisegal) **defines wire
serialization**; the project book governs concepts and rules. Everything here is
independently authored to match that wire for cross-agent league interoperability — no
simulator code is copied (it is EULA-licensed; we match field shapes only).

## Authority of every item (`M1-013`, `M1-013a`)

Each item below carries exactly one label. **No simulator behaviour is labelled
mandatory** — where the reference is our only source, the label says so.

The book labels come in two strengths, because conflating them would let a code listing
borrow a rule's sanction: **book-mandatory** means a numbered Appendix E rule *with a
stated sanction*; **book-confirmed** means the book states it (prose, formula or listing)
without attaching one. **book-minimum** is an Appendix F floor that may be raised.

| Item | Authority | Evidence |
| --- | --- | --- |
| Commit-reveal *mechanism* (SHA-256) | **book-mandatory** | Appendix E rule 17: "Use a commitment and disclosure protocol based on SHA-256. Sanction: Lack of mechanism leads to illegality of the solution" |
| Commit *byte layout* (nonce outside, behind a bar) | **simulator-derived — deviates from the book, deliberately** | See the box below. The book's `:1107` formula puts the nonce **inside**; we reproduce a real reference digest and the book's literal formula does not |
| Canonical JSON: sorted keys, `(",", ":")` | **book-confirmed** | `:1212` and `:1217` — the book's own listing writes `sort_keys=True, separators=(",", ":")`, and `:1190` says this "ensures that both peers generate an identical byte-stream". A listing, not a ruled sanction, so *confirmed* rather than *mandatory* |
| Canonical JSON: `ensure_ascii=False` | **simulator-derived** | Not specified in the book, and **not pinned by any vector** — every reference record is pure ASCII, so `True` and `False` agree there. Load-bearing the moment a hint carries an accent |
| Nonce length/format (`token_hex(16)`, 32 hex) | **simulator-derived** | The book describes a nonce only qualitatively — `:1128` "a random string… ensures uniqueness of the hash and prevents dictionary attacks". No byte count is mandated |
| Nonce kept secret until reveal | **book-mandatory** | Appendix E rule 18: "Keep the Nonce secret until the end of the game. Sanction: Disqualification due to risk of dictionary attack" |
| Tool names (`negotiate`, `receive_turn`, `submit_audit`, `receive_control`) | **Option-B project choice** | Neither name appears anywhere in the book; adopted from the reference's exposed surface per `OPTION_B_INTEROP_DECISION.md` |
| Argument names (`message` / `payload`) | **Option-B project choice** | Same; the book does not describe an MCP tool surface |
| No envelope — the argument *is* the message | **simulator-derived** | The book names the data to exchange ("their actual Move and Hint") but does not define a serialization envelope |
| `TurnMessage` field roster | **simulator-derived** | The reference's dataclass; the book lists the *content* (move, hint, intent) not the wire field names |
| Unknown/extra fields **ignored** | **simulator-derived** | Not specified in the book. The reference ignores them; `X-02` aligned both our repos after a mismatch starved a peer |
| Agreed-configuration hash over the **whole** terms object | **book-mandatory** | Appendix E rule 11: configuration "identical, bit-for-bit, on both sides. Sanction: Disqualification of the game due to lack of symmetry" |
| Identity carries **no role** | **simulator-derived** | Roles alternate across sub-games; verified against the reference 2026-07-31. The book's symmetry principle is consistent with it but does not state it |
| Scoring 20/5 capture, 5/10 survival, 2/2 tie | **book-mandatory** | Appendix F table 17, status `Fixed` |
| Scent centre 0.9, decay 0.10, 5×5 field | **book-mandatory** | Appendix F, status `Fixed` |
| Board 7×7, steps 35, barriers 14 | **book-minimum** | Appendix F, status `Minimum` — rule 12: "upload minimum values… and never lower", so raising is legal |
| `result_claim` ∈ {capture, survival, timeout} | **simulator-derived** | The reference's vocabulary; the book names the outcomes, not these tokens |
| Duplicate-key refusal, private-field refusal | **project choice** (`M1-017b`/`c`) | Derived from rule 11 and `:2901`, but the refusals themselves are ours |

### The one place we knowingly depart from the book

`:1107` states `H_commit = SHA256(State || Move || Intent || Nonce)` — the nonce **inside**
the hashed string, no delimiter. We do not do that. We hash
`canonical_json(payload) + "|" + nonce`, matching the reference.

This is a deliberate, evidenced deviation rather than an oversight, and it is the reason
this table exists. `tests/unit/test_reference_vector.py` reproduces the digest
`78a31c51…` from a real reference match log; the book's literal construction yields a
**different** digest on the same record. Following the book here would fail every
cross-peer audit against any classmate who used the simulator — which is all of them.

Rule 17 is still satisfied: it mandates *"a commitment and disclosure protocol based on
SHA-256"*, which this is. What the book fixes is the mechanism; what it also happens to
print is one byte layout, and only the mechanism carries a sanction.

**`UNKNOWN` items** are tracked in `UNKNOWN_REQUIREMENTS.md` rather than duplicated here.

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

### The `exchange_audit` confusion, twice now

A reference-code notebook asserted on 2026-08-06 that `submit_audit` was "an error" and
that `exchange_audit` "is the only registered MCP tool name". It is wrong, and it said so
while admitting the `@mcp.tool()` lines were "truncated in the excerpts" — it was reading
`infra/mcp_client.py`, the **client**.

`OPTION_B_INTEROP_DECISION.md` settled this already: `submit_audit` is the exposed server
tool; `exchange_audit` is only the reference's client-side method that calls it. The Cop
repository records the same conclusion in `ADR-001` and `OB-003`. Left here because the
confusion has now surfaced twice, and the next person to ask will be told the same wrong
thing with the same confidence.

## Messages (`protocol/wire.py`)

- **TurnMessage**: `step, sender, hint, smell_grid, commit, timestamp` (+ optional
  `barrier_placed, capture_claim, claim_response, win_claim`). `smell_grid` is a dict
  `{"r,c": intensity}`. **Ignores unknown fields** — corrected 2026-08-06: the code has used `_known_only` since the `X-02` fix, and this line still said "rejects". A classmate implementing to the old wording would have expected a refusal we no longer give.
- **ControlMessage**: `kind, sender` (+ `sub_game_number, status, step_budget, payload`).
  Ignores unknown keys (matching the sim).
- **AuditPayload**: `sender, records[{payload,nonce,commit}], result_claim` where
  `result_claim ∈ {capture, survival, timeout}`. **Ignores unknown fields** (same `X-02` correction).

## Handshake (`protocol/handshake.py`)

Each peer signs `commit_of(terms, nonce)` and verifies the opponent signed the **same**
terms. Identity is per-group and **carries no role** (roles alternate across sub-games);
it is exchanged but not signed. `config_sha256 = canonical_sha256(terms)`.

### Verified against the reference — 2026-07-31

Checked before implementing `M5-004`, per the standing rule to consult the lecturer's
`Game-P2P-Cop-Chase` notebook first. Four properties confirmed, one trap avoided.

| Property | Reference | This repo |
|---|---|---|
| Signature object | the shared agreed terms, 16-byte nonce concatenated **outside** behind `\|` | `commit_of(terms, nonce)` — same |
| `config_sha256` scope | `canonical_sha256(shared_terms)` over the **whole** terms dict, not a subset | `config_sha256()` — same |
| Role in negotiation | absent — "roles switch across the sub-games, so no role and no `sub_game_number` appear here" | `identity_block()` carries no role — same |
| Identity members | `group_id`, `group_name`, `members`, `repos`, `mcp_servers`, `llm_model`, `spec` | `identity_block()` — same seven |
| Mismatch behaviour | "refuses to play on any mismatch"; aborts "naming exactly which term is missing" | `verify_peer()` raises; `missing_required_terms()` names them |

**The trap.** One source line reads "signed terms now include `game_id`, `game_uid`,
`num_games`", which would have meant our `AGREEMENT_TERMS` was missing two keys and
every signature check against a classmate would fail. Following up established the
opposite: `game_id` and `game_uid` are **not in the negotiated terms dictionary**. They
are computed as a *pure function of shared inputs* so both peers derive identical values
with no negotiation step, and they surface only as top-level keys in the emitted
`config_*.json` and `log_*.json` artifacts.

Adding them to the signed terms would therefore have **created** the interop failure it
looked like it was preventing. `AGREEMENT_TERMS` is correct unchanged. The deterministic
derivation of the two identifiers is M7 artifact work and is still open.

## Outcome / scoring

`state.scoring.wire_result_claim(Outcome)` maps the M3 outcome to the wire claim:
`CAPTURE→capture`, `SURVIVAL→survival`, `TECHNICAL_LOSS→timeout` (the sim's 0/0 bucket).
`TIE` is series-level only. Table-17 point values already match the simulator.

## Resolved unknowns (see `UNKNOWN_REQUIREMENTS.md`)

U-002 (canonicalization), U-003 (tool surface), U-004 (handshake), U-005 (commitment),
U-014 (event ordering), U-021 (role schedule: 1/3/5 natural, 2/4/6 swapped, Thief first)
are now settled by the lecturer's authoritative answer.
