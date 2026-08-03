"""`M6-004b`: the movement decision is always pure Python — no LLM, no network.

Appendix E rule 25 and `ADR-0007` forbid the LLM from influencing a move. The move is
produced by `strategy/` from evidence prepared by `perception/`, so a guard walks both
packages and fails on any import of an LLM provider or a network carrier. The move can
therefore never depend on a model's output, whatever a future verbal layer adds elsewhere.
"""

from pathlib import Path

MOVEMENT_PACKAGES = (
    Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "strategy",
    Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "perception",
)

FORBIDDEN = (
    "openai", "anthropic", "ollama", "genai", "generativeai", "cohere", "mistralai",
    "litellm", "llm", "fastmcp", "httpx", "requests", "urllib", "socket",
)


def test_the_movement_path_imports_no_llm_or_network() -> None:
    offenders: list[tuple[str, str]] = []
    for package in MOVEMENT_PACKAGES:
        for path in package.rglob("*.py"):
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped.startswith(("import ", "from ")):
                    continue
                offenders += [(path.name, stripped) for token in FORBIDDEN if token in stripped]
    assert offenders == [], f"the movement path must be LLM- and network-free: {offenders}"
