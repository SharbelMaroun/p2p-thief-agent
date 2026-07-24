# P2P Thief Agent — Distributed Cops-and-Robbers over a P2P Network

> **Companion repository (Cop):** <https://github.com/SharbelMaroun/p2p-cop-agent>

An autonomous **Thief agent** that plays a distributed evasion game against a Cop agent over a real peer-to-peer network — no central server, no referee. Each agent is simultaneously a FastMCP server and client, perceives only partial information (scent fields + possibly-deceptive natural-language hints), and proves its own honesty via SHA-256 commit-reveal.

- **Course:** Orchestration of AI Agents — University of Haifa (Dr. Yoram Segal), Final Project
- **Model:** Dec-POMDP · **Network:** FastMCP P2P + tunnel · **Integrity:** commit-reveal + mutual audit
- **Status:** Phase 0 — documentation & scaffold (see [`docs/TODO.md`](docs/TODO.md))

---

## Academic Report

*The six mandatory report sections (rulebook Ch.9) — completed as the build progresses:*

### 1. Selected Dec-POMDP model
*(to be written — see [`docs/PRD.md`](docs/PRD.md) §1 for the current formulation)*

### 2. FastMCP communication dilemma
*(to be written — queues, failure handling, Orchestrator + Gatekeeper; see [`docs/PLAN.md`](docs/PLAN.md))*

### 3. Implemented strategy
*(to be written — belief-driven evasion heuristics; see [`docs/PRD_strategy.md`](docs/PRD_strategy.md))*

### 4. Learning curves
*(only if RL is used — currently out of scope, see PRD §6)*

### 5. Screenshots
*(to be added — Live GUI belief map + Replay Viewer "Verified OK")*

### 6. Companion repository
The Cop agent lives at **<https://github.com/SharbelMaroun/p2p-cop-agent>** — the two agents run as fully separated processes with separate config directories (Zero-Trust mandate, rulebook Ch.2).

---

## Installation

*(scaffold pending — `uv` only, per submission guidelines §8.4)*

```bash
git clone https://github.com/SharbelMaroun/p2p-thief-agent
cd p2p-thief-agent
uv sync
```

## Usage

*(pending — will follow the pattern below)*

```bash
uv run python -m <pkg> peer --role thief
uv run python -m <pkg> replay --log logs/<log-file>.json
```

## Configuration

- `config/thief/game.json` — **shared, signed** game contract (Appendix F values; byte-identical for both peers)
- `config/thief/game.toml` — **private** per-peer settings (port, opponent URL, strategy class, LLM provider)
- `config/thief/rate_limits.json` — Gatekeeper limits
- Secrets go in `.env` (never committed) — see `.env-example`

## Documentation

Full documentation suite in [`docs/`](docs/): [PRD](docs/PRD.md) · [PLAN](docs/PLAN.md) · [TODO](docs/TODO.md) · per-mechanism PRDs ([commit-reveal](docs/PRD_commit_reveal.md), [scent & belief](docs/PRD_scent_belief.md), [strategy](docs/PRD_strategy.md), [P2P/MCP](docs/PRD_p2p_mcp.md), [gatekeeper & reporting](docs/PRD_gatekeeper_reporting.md)) · [prompt log](docs/PROMPTS.md)

## License

[MIT](LICENSE) — educational project. Game specification © Dr. Yoram Segal (course materials, not included here).
