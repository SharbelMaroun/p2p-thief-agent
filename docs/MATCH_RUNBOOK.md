# Match runbook — playing a real opponent

The one page to follow when sitting down with a classmate. Every step here was
exercised end to end on 2026-08-08: two OS processes negotiated, played 35
commit-reveal turns, agreed on the outcome, and the log replayed `Verified OK`.

## Before the match (both teams together)

1. **Agree the shared match file.** One `game.json`, **byte-identical** on both
   machines (Appendix F obligation 1). Copy one file — do not retype it. Verify:

   ```powershell
   Get-FileHash game.json -Algorithm SHA256   # must print the same hash on both machines
   ```

   The file must carry the real league values — `num_games: 6`, `max_moves: 35`,
   `max_barriers: 14`, the agreed starts — and `agreed_between` must name **both
   group ids exactly** as each team's private config spells them (a mismatch refuses
   the match before move one; we hit this in rehearsal).

2. **Each team fills its private `game.toml`** (never shared, never committed):
   `[game]` group identity, members, repo URLs; `[network]` `my_port`,
   `opponent_url` (their tunnel address), `public_url` (your tunnel address);
   `[llm]` model; `[hardware]` **true** specs — they are sealed in Step-0 and
   forging forfeits the fairness bonus (rule 24).

3. **Open the tunnels** (rule 10 — mandatory; localhost does not count for the
   league, p. 97/215): `ngrok http 8801` on the Thief machine, exchange the public
   URLs, put each other's URL in `opponent_url`.

4. **Declare game history**: the count of counted games played so far is declared at
   match start (rules 37–38; a false declaration is absolute disqualification). The
   Cop side's declaration artifact carries it automatically from `results/` — check
   it is current.

## Running one sub-game (Thief side — this repository)

```powershell
uv run p2p-thief serve --peer <their-mcp-url> --port 8801 `
    --game game.json --private config\thief\game.toml `
    --threshold 35 --sub-game 1 --artifacts games\artifacts
```

`--game` makes the match **negotiated**: signed flat terms projected from the shared
file, rule-24 identity on the offer, refusal-by-name on any mismatch, and play to the
negotiated horizon. `--sub-game N` numbers the artifacts (`log_<game_id>_g0N.json`).

Healthy start looks like: FastMCP binds → "playing <url>" → ~35 turns of traffic →
`match finished: Outcome.SURVIVAL after 35 step(s)` (or a capture) → `log written`.

## The six-sub-game series

The lecturer's ruling: sub-games **1, 3, 5** use the natural roles, **2, 4, 6** the
swapped roles. Each sub-game is one `serve` run of the right repository on each side,
with `--sub-game` set to its number:

| Sub-game | Our peer   | Their peer |
|---------:|------------|------------|
| 1, 3, 5  | this Thief | their Cop  |
| 2, 4, 6  | our Cop    | their Thief|

Fresh state every sub-game (new process = new belief, new barriers, new trail — rule
2 forbids carrying anything across).

## After the match (both teams)

1. **Verify the log immediately**, in front of each other:

   ```powershell
   uv run p2p-thief replay --log games\artifacts\log_<game_id>_g01.json
   # must print: Verified OK — N steps re-verified
   ```

2. **Reconcile outcomes** — both sides' logs must state the same result and winner;
   conflicting reports score 0/0 for both (`[AE-35]`, `M9-021a`).
3. **Send the JSON end-of-game report** to the lecturer's address (rule 51 — a game
   without the report is not credited). Addresses per `docs/RUNBOOK_reporting_setup.md`.
4. **Commit the artifacts** under the agreed names (Appendix F obligation 4) and take
   the mandatory screenshots: Live GUI belief map + Replay `Verified OK` (p. 81/189).

## Run preflight on their file the moment it arrives

```powershell
uv run p2p-thief preflight --match <their-game.json> --private config\thief\game.toml
```

Do this **before** agreeing a time, not on match day. It now checks the two things that
refuse a match at the handshake, and both were live defects in the first file group
`uoh-ay26` sent us on 2026-08-11:

- `participants` — `agreed_between` must name our `group_id`. Theirs said
  `["cop", "thief"]`: the two *roles*. Appendix B prints the two **group ids**
  (`inst/police_thief_p2p_Summary.md:2928`).
- `schema version` — must be `1.2`. Theirs said `"1.00"`, the guidelines' config
  revision, which is a **different key** (the optional `version`). The reference
  simulator ships `"1.3"`, so agree the value in writing; see `C-027`.

Until that day preflight printed **`ready`** for that file — the terms projection reads
neither field — and the refusal only landed mid-handshake with the opponent waiting.

## Troubleshooting (each of these cost us a rehearsal run)

- `offering group '<id>' is not in agreed_between` — the shared file's
  `agreed_between` does not name that team's exact `group_id`.
- `502` from the opponent's URL — Cloudflare (or ngrok) is up but **their** tunnel is
  not running; that is a peer-not-started, not a network fault. `peer_answers` reports
  it as not-ready rather than treating the socket as proof of life.
- `Unexpected UTF-8 BOM` — the shared file was saved with a BOM (PowerShell's
  `Out-File` does this); re-save as plain UTF-8.
- Technical loss at step 1 on both sides — one peer is not actually reachable at the
  URL the other dialled; re-check tunnels and `opponent_url`.
- `agreed terms differ on: <term>` — the two machines hold different shared files;
  re-copy and re-hash.
