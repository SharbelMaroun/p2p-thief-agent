# Installation and usage

Covers `M9-012`, `M9-012a`…`M9-012e`.

## What runs, and what still does not

`M9-025` closed on 2026-08-07: **the agent now has a command-line runtime.** `p2p-thief
serve` starts this peer's mailbox, and `p2p-thief replay` / `verify` re-check a stored match
from a terminal — rule 20's threshold condition, without opening a test file.

**Still not possible from the command line: playing a full counted game.** `serve` binds the
mailbox and waits; it does not negotiate terms and start a series on its own. That is
deliberate rather than unfinished — this peer *opens* every turn cycle, since the book gives
the Thief the first move, so a launcher that began playing the moment it started would race
an opponent still binding its own port. Terms have to be negotiated before there is an
address to open against.

Until that handshake is wired, a full series runs through `tests/integration/`, which is
where it is exercised today.

## System requirements — `M9-012a`

| Requirement | Value |
| --- | --- |
| Python | ≥ 3.11 (`pyproject.toml`); developed and tested on 3.12/3.13 |
| Package manager | [`uv`](https://docs.astral.sh/uv/) — the lockfile is the install contract |
| OS | **Windows 11 only.** Never run on Linux or macOS (`M9-013a` open) |
| Git | Required. The history scanner and the commit-provenance resolver both shell out to it |
| Network | Not needed for any test. Every external call is injected and doubled |

```bash
git clone https://github.com/SharbelMaroun/p2p-thief-agent
cd p2p-thief-agent
uv sync --frozen
```

`--frozen` is deliberate: it installs exactly `uv.lock` and fails rather than silently
resolving a newer dependency. A run that resolves freely is not the run the gates passed.

## Run modes and flags — `M9-012b`

### The peer

```bash
uv run p2p-thief serve                      # bind 127.0.0.1:8801, wait for an opponent
uv run p2p-thief serve --port 8802          # a second peer on one machine
uv run p2p-thief serve --host 0.0.0.0       # reachable off-machine; loopback is the default
uv run p2p-thief serve --name my-thief      # the name reported to the peer
```

The bind default is **loopback, not `0.0.0.0`**: exposing a mailbox to the network should be
something you typed, not something you inherited.

### Verifying a match — rule 20

```bash
uv run p2p-thief replay --log logs/log_demo_g01.json    # prints the banner
uv run p2p-thief verify --log logs/log_demo_g01.json    # silent; exit 1 if TAMPERED
```

`replay` prints the `Verified OK` / `TAMPERED` banner — this is the source of the screenshot
p.81/189 calls absolute mandatory. `verify` is the same check with an exit code instead of
output, so it can sit in a pipeline. Both load **by path**, which is rule 36's mutual-audit
posture: they work unchanged on an opponent's log.

Exit codes are distinct on purpose: `0` verified, `1` tampered, `2` could not be read. An
operator seeing `1` should reach for the evidence; seeing `2`, for their shell history.

### The package itself

```bash
uv run p2p-thief --help
uv run p2p-thief --version       # works with no transport installed
```

### Quality gates

```bash
uv run ruff check .                              # lint, pinned select set
uv run python -m pytest -q                       # 1591 tests, 85% branch floor
uv run python scripts/check_file_lengths.py      # 150-line cap
uv run python scripts/check_secrets.py           # working tree
uv run python scripts/scan_git_history.py        # every blob in history
uv run python scripts/check_submission_contents.py
uv run python scripts/check_artifacts_committed.py
uv run python scripts/verify_clean_clone.py      # all of the above, in a fresh clone
```

`verify_clean_clone.py` is the one worth running before any submission: it clones `HEAD`,
installs frozen, and re-runs the gates there. A gate script that lives untracked in your
working tree passes everywhere except in the clone.

### Evidence and figures

```bash
uv run python scripts/run_experiments.py            # arena runs, writes results/
uv run python scripts/render_charts.py              # SVG figures
uv run python scripts/benchmark_decision.py         # per-decision timing
uv run python scripts/strategy_comparison.py        # baseline vs belief policy
uv run python scripts/capture_live_gui_screenshot.py    # rule 20 evidence
uv run python scripts/capture_replay_screenshots.py     # "Verified OK" evidence
```

### Playing a game

Through the integration suite, which is currently the only way:

```bash
uv run python -m pytest tests/integration/test_rehearsal.py -q          # full series
uv run python -m pytest tests/integration/test_localhost_two_processes.py -q   # two processes
uv run python -m pytest tests/integration/test_replay_of_stored_match.py -q    # replay off disk
```

## Configuration — `M9-012c`

| Path | Effect | Committed? |
| --- | --- | --- |
| `config/thief/` | Board, movement, scoring, pheromone and rate-limit parameters — the negotiated Appendix F values | Yes |
| `config/game.toml` | **Private** local settings. Gitignored | No — rules 39/40 |
| `config/*.private.toml` | Any local override | No |
| `games/<game_id>/` | Each counted game's config, committed per Appendix F obligation 4 | Yes, deliberately |
| `.env` | Credentials. Gitignored; `.env-example` documents the names without values | No |
| `credentials.json`, `token.json` | Gmail OAuth. Gitignored, and refused by the history scanner **by name** | No |

The split matters: a shared config that leaked a strategy or model field would breach rule 2,
so `protocol/outbound_fields.py` matches on **key names** and refuses them before anything is
sent. See `docs/RUNBOOK_reporting_setup.md` for the Gmail setup.

## Troubleshooting — `M9-012d`

| Symptom | Cause | Fix |
| --- | --- | --- |
| `REFUSING TO SCAN: this is a shallow clone` | `git clone --depth 1`, or CI without `fetch-depth: 0` | `git fetch --unshallow`. The scan is meaningless on a truncated clone, which is why it refuses instead of reporting OK |
| `uv sync --frozen` fails | Lockfile and manifest disagree | `uv lock` then re-run the gates; do not install unfrozen to get past it |
| `no Gmail credential at …` | Consent flow not run | `docs/RUNBOOK_reporting_setup.md` step 3 |
| `there is no refresh token` | Consent granted without offline access | Delete `token.json`, re-run consent |
| `refusing to compose a report for a settlement in state …` | The audit failed, or the opponent disagreed | Do **not** send. Preserve the logs and raise it with the lecturer — sending would turn their rule 19 loss into a shared rule 35 loss |
| `the working tree has uncommitted changes` | Provenance check before a counted game | Commit or stash. The recorded commit must contain the code that plays |
| `a log summary with no end time` | Building a log mid-game | Only build after the game ends; nonces stay secret until then |
| Secret scan flags a line | A value that looks live | Change the value to a recognised placeholder (`dummy-…`, `${VAR}`, `<replace me>`). Do **not** allowlist |
| `only N objects — is --all still passed?` | Shallow checkout in a test run | Same fix as the first row |

## Licence and attributions — `M9-012e`

**MIT License**, © 2026 Sharbel Maroun and contributors. Full text in `LICENSE`.

Runtime dependencies, all under permissive licences (MIT/BSD/Apache-2.0), pinned in
`uv.lock`:

| Package | Role |
| --- | --- |
| `fastmcp` | The peer-to-peer transport the book mandates |
| `pydantic` | Wire-message validation |
| `uvicorn`, `starlette` | ASGI serving for the local peer |
| `httpx` | Client transport under FastMCP |

Development-only: `pytest`, `pytest-cov`, `ruff`, `beartype`.

No third-party code is vendored into `src/`. Course material in `inst/` belongs to
Dr. Yoram Segal and is quoted under fair academic use, cited by page throughout the docs.
