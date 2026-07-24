# Simulator Baseline

- Intended upstream: <https://github.com/rmisegal/Game-P2P-Cop-Chase>
- Local path:
  `C:\Users\amrsa\OneDrive\Desktop\OrchAI\FinalProject\SimulatorEXM-Repo\Game-P2P-Cop-Chase`
- Inspection date: 2026-07-24
- Upstream commit: `UNKNOWN`

The simulator directory is nested in another Git worktree. `git rev-parse HEAD` resolves
to parent-planning-repository commit `6c1e8fa279e5a29dcfae5883435aa5afd56976d1`,
whose remote is `https://github.com/AmrSafadi/AI-Agent-Orchestration-FinalProject.git`.
That is not evidence of the lecturer simulator’s upstream commit.

## Relevant inspected files and symbols

| File | Symbols/observations | Use |
|---|---|---|
| `src/police_thief/infra/mcp_server.py` | FastMCP server/tool handlers | Illustrative only |
| `src/police_thief/infra/mcp_client.py` | Peer calls/retry behavior | Illustrative only |
| `src/police_thief/domain/protocol.py` | `TurnMessage`, `ControlMessage`, `AuditPayload` | Illustrative only |
| `src/police_thief/domain/crypto.py` | canonicalization, `CommitReveal`, `audit_records` | Illustrative only |
| `src/police_thief/domain/brains.py` | `ThiefBrain`, `PoliceBrain` | Illustrative only |
| `src/police_thief/sdk/series.py` | `role_for`, `run_series`, configured count | Illustrative only |
| `src/police_thief/report/artifacts.py` | Artifact builders | Illustrative; official templates absent |
| `config/{police,thief}/game.json` | Example shared values | Never binding |
| `config/{police,thief}/game.toml` | Ports, reporting mode, strategy selectors | Example/local choices |

## Test

Command (with writes redirected into this repository):

```text
uv run --project <simulator-path> pytest -q <simulator-path>/tests
  -p no:cacheprovider --basetemp .tmp-simulator-pytest
```

Actual result: exit code 1 and six failures in `tests/unit/test_artifacts.py`.
Each was `FileNotFoundError` for an expected file under the sibling
`SimulatorEXM-Repo/Json-examples/` directory. All other collected tests passed.

The overview’s earlier “246 passed, 7 failed” is stale or from a different state and is
not the current result. The simulator was not copied, modified, or made a dependency.
A clean upstream checkout at a recorded commit is required before relying on exact
illustrative behavior; official sources must still confirm every requirement.
