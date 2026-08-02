"""`M5-018`: the public SDK imports no transport, so it never drags a socket in.

The SDK is the one boundary every adapter, CLI, and future GUI reaches through
(`PS-007`). Transport lives in `adapters/`, behind that boundary. If the SDK itself
imported FastMCP or a peer connector, importing the SDK would pull a socket stack into
a process that only wanted the domain, and a unit test of the public surface would
suddenly need a network. Two guards keep it honest: a static walk of the package, and
a fresh interpreter that imports the SDK and proves no transport stack reached
`sys.modules`.
"""

import subprocess
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "sdk"

FORBIDDEN = ("fastmcp", "adapters", ".peer", "orchestration", "socket", "httpx", "requests")


def test_sdk_package_imports_no_transport() -> None:
    """No module under `sdk/` may name a transport carrier in an import line."""
    offenders: list[tuple[str, str]] = []
    for path in SDK.rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith(("import ", "from ")):
                continue
            offenders += [(path.name, stripped) for token in FORBIDDEN if token in stripped]
    assert offenders == [], f"SDK must be transport-free: {offenders}"


def test_importing_the_sdk_pulls_in_no_socket_stack() -> None:
    """The strongest proof: a fresh interpreter importing the SDK never loads FastMCP.

    Run in a subprocess so an unrelated test that already imported an adapter cannot
    mask the leak through a shared `sys.modules`.
    """
    code = (
        "import sys, p2p_thief_agent.sdk;"
        "leaked=[m for m in sys.modules if m.split('.')[0] in {'fastmcp','httpx','requests'}];"
        "assert not leaked, leaked;"
        "print('clean')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "clean"
