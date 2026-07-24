# PRD — API Gatekeeper & Automated Reporting

- **Version:** 1.01 · **Status:** DRAFT · *(v1.01 — compliance audit: result JSON carries all four repo links, rule 49)*
- **Modules:** `shared/gatekeeper.py`, `shared/rate_limiter.py`, `infra/email_sender.py`, `report/*` · **Phase 7** · **Tasks:** T408-459 · **Requirements:** FR-18, FR-19, FR-20

## 1. Purpose
Report every game's result to the lecturer automatically and safely. An autonomous agent that fires unbounded Gmail calls could spam, hit rate limits (429), or get the account blocked — so **all external calls pass through one Gatekeeper**, and results are packaged as **signed JSON artifacts**.

## 2. Theoretical background
- **Gatekeeper pattern** (Watchdog family): a single doorway that enforces limits, queues, retries, and logs — implementing **backpressure** and **circuit-breaker** principles.
- **Token-bucket rate limiting:** `tokens ← min(C, tokens + r·Δt)`, allow iff `tokens ≥ 1`; separates average rate (`r`) from burst capacity (`C`).
- **OAuth 2.0 least privilege:** scope `gmail.send` only; short-lived access token + long-lived refresh token; secrets never in code.

## 3. Functional requirements
### 3.1 Gatekeeper (`gatekeeper.py`, `rate_limiter.py`)
- **GK-1** Every external (LLM/email) call goes through `execute()` — no direct calls.
- **GK-2** Limits read from `rate_limits.json` (never hardcoded): 30 rpm, 2 concurrent, 5s backoff, 3 retries, queue depth 100.
- **GK-3** Three guards: **Quota Manager** (daily cap), **Token Bucket** (rate), **DOS Detector** (loop/burst → LOCKED).
- **GK-4** Overflow is **queued (FIFO), not rejected**; backpressure alert when full; drain on reset.
- **GK-5** Retry transient failures; respect **429** (back off, don't hammer).

### 3.2 Reporting (`email_sender.py`, `report/*`)
- **RP-1** Emit the **4 JSON artifacts**: `declaration_*`, `config_*_g<NN>`, `log_*_g<NN>`, `result_*` (shared `game_uid`, names from `game_id`).
- **RP-2** Email the **result JSON as an attachment** (not plaintext) to `rimesegal+uoh26finalgame@gmail.com`.
- **RP-3** OAuth send-only (`gmail.send`); `credentials.json`/`token.json` git-ignored; `mode=draft` for testing.
- **RP-4** **Both teams send separately**; a missing report → no points even for a winner.
- **RP-5** Report includes **all four GitHub links** — two per team, ours **and** the opponent's (rule 49: "four links in the JSON files of the two teams"; opponent's repos come from the handshake identity exchange) — plus per-game commit hash and total tokens consumed.
- **RP-6** The declaration carries a truthful **games-played count** vs this opponent (false declaration disqualifies the project).
- **RP-7** Both teams **agree the result before reporting**; conflicting reports disqualify the game (0/0 for both). Official series length: **6 sub-games** (`network_and_league.num_games`, Fixed).

## 4. Interface (I/O)
```python
ApiGatekeeper(config, service).execute(api_call, *args) -> Any
ApiGatekeeper.get_queue_status() -> {queue_depth, calls_total, failures_total}
TokenBucket(capacity, refill_rate).allow(cost=1.0) -> bool
EmailSender(config).send_report(result_json: dict, subject: str) -> {sent, reason}
emit_series(config, logs_dir, series) -> result_json
```

## 5. Performance metrics
- 0 account blocks / unhandled 429s. · Burst beyond capacity is queued, never crashes. · All 4 artifacts validate against their schemas and against the sample-run format.

## 6. Constraints & limitations
- Requires a Google Cloud project + OAuth consent (Appendix A, 5 steps). · Refresh token grants months of autonomy — treat as a secret. · Reports are trust-based on game-count declaration; a false declaration disqualifies.

## 7. Alternatives considered
| Option | Verdict |
|---|---|
| Direct SMTP with app password | Rejected — password in code; no scoping. |
| Direct Gmail calls without gatekeeper | Rejected — spam/429/ban risk (§9.3). |
| Manual result submission | Rejected — rulebook mandates automation. |
| **Gatekeeper + OAuth `gmail.send` + JSON artifacts** | **Selected** — safe, scoped, book-mandated. |

## 8. Success criteria
- A full series emits all 4 valid JSON artifacts. · Result JSON is emailed (draft in dev). · A simulated burst/loop is throttled (queued/LOCKED), account safe. · 429 handled with backoff.

## 9. Test scenarios (→ T419-420, T438-439, T456-457)
- Token bucket allows then blocks under burst. · Overflow queues to configured depth. · DOS pattern → LOCKED. · `send_report` builds correct MIME + base64url (API mocked). · Artifacts validate vs schema + golden sample. · 429 → backoff, not resend-storm.
