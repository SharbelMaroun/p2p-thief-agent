"""Our advertised tunnel address, and why only the address travels (`M5-005b`).

Book §2.4 (p.13): "running servers on localhost is permitted only during the early
development stages. In practice, each group must expose its FastMCP server to the public
internet using tunneling tools, such as ngrok or Localtonet." §2.4.1 explains why — a laptop
behind NAT is unreachable, and the tunnel performs the traversal.

Separate from `private_config` because this is a different question. That module answers
*what may live in the private file*; this answers *what we advertise and what we must never
advertise with it*. The provider that produced the URL, and the token that authorises it,
stay local — rule 39 forbids pushing secrets even to a private repository, and an ngrok
authtoken inside a negotiated config would be exactly that `[AE-10]`.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from p2p_thief_agent.shared.private_config import (
    DIALABLE_SCHEMES,
    NETWORK_SECTION,
    PUBLIC_URL_KEY,
    PrivateConfigError,
    load_private_config,
)


def public_url(config: Mapping) -> str:
    """Return `[network].public_url` -- our own tunnel address, advertised to the peer.

    Book §2.4 (p.13): "running servers on localhost is permitted only during the early
    development stages. In practice, each group must expose its FastMCP server to the public
    internet using tunneling tools, such as ngrok or Localtonet." §2.4.1 gives the reason —
    a laptop behind NAT is not reachable, and the tunnel performs the traversal.

    **Only the resulting URL is exchanged.** Which provider produced it, and the token that
    authorises the tunnel, stay in this private file and never reach the shared signed object.
    Rule 39 forbids pushing secrets even to a private repository, and an ngrok authtoken in a
    negotiated config would be exactly that — so the provider choice is deliberately
    unobservable in the protocol `[AE-10]`.

    This is the value that populates the negotiation identity's `mcp_servers`.
    """
    section = config.get(NETWORK_SECTION)
    if not isinstance(section, Mapping):
        raise PrivateConfigError(f"private config has no [{NETWORK_SECTION}] section")
    value = section.get(PUBLIC_URL_KEY)
    if not isinstance(value, str) or not value.strip():
        raise PrivateConfigError(
            f"[{NETWORK_SECTION}].{PUBLIC_URL_KEY} must be a non-empty string; league play "
            "needs a public tunnel address, not a loopback one (book §2.4)")
    url = value.strip()
    if not url.startswith(DIALABLE_SCHEMES):
        raise PrivateConfigError(
            f"[{NETWORK_SECTION}].{PUBLIC_URL_KEY} must be http(s), got {url!r}")
    if _is_loopback(url):
        raise PrivateConfigError(
            f"[{NETWORK_SECTION}].{PUBLIC_URL_KEY} is a loopback address ({url!r}). An "
            "opponent cannot reach it, and advertising it would let the game fail at the "
            "handshake rather than here. Localhost is permitted only in early development "
            "(book §2.4)")
    return url


def _is_loopback(url: str) -> bool:
    """Whether a URL points back at this machine.

    Checked because the failure it prevents is silent and late: a loopback address is a
    perfectly valid URL, the peer accepts it during negotiation, and the first turn simply
    never arrives. The book calls binding `127.0.0.1` the one-word bug no local test catches.
    """
    host = url.split("//", 1)[-1].split("/", 1)[0].rsplit("@", 1)[-1]
    host = host.rsplit(":", 1)[0].strip("[]").lower()
    return host in {"localhost", "127.0.0.1", "0.0.0.0", "::1", ""} or host.startswith("127.")


def load_public_url(path: str | Path) -> str:
    """Read our advertised tunnel address from one explicit private TOML path."""
    return public_url(load_private_config(path))
