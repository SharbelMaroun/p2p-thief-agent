"""`M7-003a`: no service calls an external API directly — all route through the gatekeeper.

Guidelines §5.1 requires every external API call (Gmail, LLM providers) to pass through the
one centralized gatekeeper, so the rate limiter, quota, and DOS gates cannot be bypassed. No
such provider is wired yet; this guard walks `src/` and fails on any direct import of one, so
when the Gmail (`M7-005`) and verbal (`M7-004`) paths are built they must go through the
gatekeeper rather than reach out on their own. The FastMCP peer transport is not an external
*API* in this sense — it is the opponent link, guarded separately (`M5-002b`).
"""

from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent"

EXTERNAL_APIS = (
    "googleapiclient", "google.oauth2", "google_auth", "google.generativeai", "smtplib",
    "openai", "anthropic", "ollama", "cohere", "mistralai", "litellm",
)


def test_no_module_calls_an_external_api_directly() -> None:
    offenders: list[tuple[str, str]] = []
    for path in SRC.rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith(("import ", "from ")):
                continue
            offenders += [(path.name, stripped) for token in EXTERNAL_APIS if token in stripped]
    assert offenders == [], f"external API calls must route through the gatekeeper: {offenders}"
