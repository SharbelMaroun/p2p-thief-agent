"""`M4-013`: the protocol layer imports no transport, so it runs over any carrier.

Commit-reveal, canonicalization, sealing, the handshake, and attestation must work the
same over a socket, an in-memory queue, or a replay from disk. A transport import in
this layer would couple the cryptography to one carrier and make it untestable without
a network — so a guard walks the package and fails on any such import.
"""

from pathlib import Path

PROTOCOL = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent" / "protocol"

FORBIDDEN = ("fastmcp", "adapters", ".peer", "socket", "httpx", "requests", "urllib")


def test_protocol_layer_imports_no_transport() -> None:
    offenders: list[tuple[str, str]] = []
    for path in PROTOCOL.rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith(("import ", "from ")):
                continue
            offenders += [
                (path.name, stripped) for token in FORBIDDEN if token in stripped
            ]
    assert offenders == [], f"protocol layer must be transport-free: {offenders}"


def test_gitattributes_pins_lf_on_controlled_files() -> None:
    """`M4-011a`: CRLF would break every hash, so controlled files are LF-normalized."""
    attrs = (PROTOCOL.parents[2] / ".gitattributes").read_text(encoding="utf-8")
    assert "* text=auto eol=lf" in attrs
    for ext in ("*.json", "*.py", "*.toml"):
        assert f"{ext} text eol=lf" in attrs
