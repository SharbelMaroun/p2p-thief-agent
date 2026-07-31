# Verified Parameters Baseline

Status: direct Appendix F evidence from official book v3.0.0.

The official PDF has SHA-256
`7c9e1d7527582c3aef9afd71709981cea50ea60b8fabefe85efccab0a5fdd02e`.
Values below are verified defaults with their official status; this document does not
create an active config or claim Cop/Thief byte parity.

`FIXED` values cannot change. `MINIMUM` values may move only in the harder direction by
agreement. `NEGOTIATED` values use the shown default absent a different agreement.

| Area | Parameter | Value | Status | Direct source |
|---|---|---:|---|---|
| Board | Grid size | `7×7` | `MINIMUM` | Appendix F Table 13, PDF p.152 |
| Board | Agents | `2` | `FIXED` | Table 13 |
| Board | Origin / first index | top-left / `0` | `NEGOTIATED` | Table 13 |
| Board | Thief / Cop start | `(3,3)` / `(0,0)` | `NEGOTIATED` | Table 13 |
| Verbal | Area / hint words | New York / `15` | `NEGOTIATED` | Table 14, PDF p.152 |
| Movement | Moves | `N,S,E,W,STAY`; no diagonal | `FIXED` | Table 15, PDF p.153 |
| Movement | Barriers / max steps / survival | `14` / `35` / `35` | `MINIMUM` | Table 15 |
| Scent | Center / decay / field | `0.9` / `0.10` / `5×5` | `FIXED` | Table 16, PDF p.153 |
| Score | Capture, Cop / Thief | `20` / `5` | `FIXED` | Table 17, PDF p.154 |
| Score | Survival, Cop / Thief | `5` / `10` | `FIXED` | Table 17 |
| Score | Tie / technical loss | `2` each / `0` | `FIXED` | Table 17 and Appendix E rule 19 |
| League | Sub-games per series | `6` | `FIXED` | Table 18, PDF p.154 |
| League | Diversity / pass minimum / group maximum | `10` / `2` / `10` | `FIXED` | Table 18 |
| League | Token estimate per series | approximately `200000` | `NEGOTIATED` | Table 18 |
| Gatekeeper | Requests/minute / concurrency | `30` / `2` | `MINIMUM` | Table 19, PDF p.155 |
| Gatekeeper | Retry delay / retries / queue | `5 s` / `3` / `100` | `MINIMUM` | Table 19 |
| Gatekeeper | Response / watchdog timeout | `30 s` / `60 s` | `NEGOTIATED` | Table 19 |
| Reporting | General address | `rmisegal@gmail.com` | official address | Table 20, PDF p.157 |
| Reporting | Automated report address | `rmisegal+uoh26finalgame@gmail.com` | official address | Table 20 |
| Verbal mode | Provider modes | `template`, `ollama`, `claude_api`, `claude_cli` | private choice | Table 21, PDF p.158 |

Official filenames are `declaration_<game_id>.json`,
`config_<game_id>_g<NN>.json`, `log_<game_id>_g<NN>.json`, and
`result_<game_id>.json` (Appendix F Table 20).

The book's Chapter 4.3 formula applies multiplicative decay:
`τ(t+1) = max(0, (1-ρ) × τ(t) + Δτ)`. Exact observation and turn ordering still require
an accepted contract. Do not copy the simulator's subtractive implementation.

**Table 19 status detail, verified against the book PDF 2026-08-01.** The rate/concurrency, retry-delay, retry-count and queue rows are `MINIMUM`; the **watchdog timeout for deadlock detection (60 s) is `NEGOTIATION`**, not `MINIMUM`. The distinction matters because a `MINIMUM` may only be made stricter, whereas a negotiated value may move either way by agreement. The response timeout (30 s) and watchdog timeout live in `network_and_league`; the retry and queue limits live in `rate_limiter_gatekeeper` — all in the **shared, signed** match object, so neither peer can give itself a longer rope.
