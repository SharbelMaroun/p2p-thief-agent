# Committed game configurations

Every game's configuration artifact is committed here, one directory per `game_id`:

```
games/<game_id>/config_<game_id>_g<NN>.json
```

## Why this directory is not in `.gitignore`

Appendix F's fourth obligation requires each game's configuration to be committed to the
repository, so any past game can be reproduced from what is checked in rather than from
whatever survives on the machine that played it.

`.gitignore` excludes `logs/`, `reports/generated/` and `results/generated/`. That is the
right default for run output and exactly wrong for the one artifact an obligation says to
commit — an artifact written under an ignored path is retained on one laptop and lost to the
repository, and the failure is silent: the write succeeds and the file is present.

`src/p2p_thief_agent/reporting/retention.py` refuses to store a config under an ignored
path, and `tests/unit/test_retention.py` fails if `games/` is ever added to `.gitignore`.
The realistic way this regresses is somebody tidying the working tree, which is the same
reasoning that put `logs/` there in the first place.

## Why committing these is safe under rule 39

Rule 39 (Prohibited) forbids pushing secrets and credentials to the repository "even if it
is private and shared only with the lecturer". What lands here is the **negotiated match
config** — board size, movement rules, scoring, pheromone parameters, rate limits — and
nothing else.

That holds because `protocol/config_integrity.py` and `protocol/outbound_fields.py` keep
strategy, LLM, language and credential fields out of the shared config in the first place,
matching on **key names rather than values**. The two rules are satisfiable at once only
because those guards run before anything reaches this directory.

## What is not here, and a correction

Only the **config** carries the Appendix F obligation (obligation 4, p.140/288). The final
result's obligation is to be *emailed* (rule 51), and the game log has no explicit commit
requirement in §9.4.1's minimum-contents list — though it is needed to run the Replay app,
which is itself a threshold condition for submission (p.129/272). So logs and results are
retained under `logs/` and `results/generated/` unless a specific game's evidence is being
promoted deliberately.

**An earlier version of this file gave the wrong reason for that.** It said committing logs
would put nonces into git history, "and git history has no end". That reasoning is wrong.
Rule 18 (`inst/:3354`) requires the nonce secret **until the end of the game**, and the book
defines Step 4 as the Final Reveal: "Only at the end of the game are all values, including
the Nonce, revealed for a full mutual audit" (`inst/:1136`, `:1155`). Once the game ends the
secrecy obligation *expires* — the revealed nonces are precisely what lets a third party
recompute every commitment, which is the point of publishing them.

Committing a **finished** log is therefore permitted. What is still forbidden is building or
sharing a log while the game is in play, which `build_log` refuses by requiring `ended_at`.

## What is committed here today

`game-593df753457f/` is a **real two-process match** played on 2026-08-08 between this team's
Cop and this team's Thief over a socket -- an engineering rehearsal, **not** a counted league
game against a classmate, and it is never reported as one.

| File | Why it is here |
|---|---|
| `config_game-593df753457f_g01.json` | Appendix F obligation 4: the configuration of every game is committed. |
| `declaration_game-593df753457f.json` | The pre-game declaration, including the commit hash the game ran under (rule 53). |
| `log_game-593df753457f_g01.json` | This peer's revealed log. **Not obligated** -- the log is absent from the section 9.4.1 minimum-contents list -- but committed deliberately: it is the subject of the mandatory `Verified OK` screenshot, and a screenshot of a file nobody else can open proves nothing. |
| `log_game-593df753457f_g01.opponent.json` | The opponent's revealed log, so the mutual audit (rule 36) and the replay viewer's two-trail board can both be reproduced from the repository. |

Confirmed against the book before committing: the **config** carries the commit obligation;
the **log** does not, but nothing forbids committing a finished one. Rule 18 keeps a nonce
secret *until the end of the game*, and these games are over, so the revealed nonces here are
exactly what lets a third party recompute every commitment -- which is the point.

Both logs verify under **both** peers' verifiers:

```text
uv run p2p-thief replay --log games/game-593df753457f/log_game-593df753457f_g01.json
```
