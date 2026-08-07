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

## What is not here

Logs and results stay under `logs/` and `results/generated/`. Only the config carries the
Appendix F obligation, and committing per-step logs for every game would put nonces into git
history — rule 18 keeps those secret until the end of the game, and git history has no end.
