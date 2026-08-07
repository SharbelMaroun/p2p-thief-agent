"""`M5-005a` / `M5-005b`: advertise a tunnel address, and never the token behind it.

Book §2.4 (p.13): "running servers on localhost is permitted only during the early
development stages. In practice, each group must expose its FastMCP server to the public
internet using tunneling tools, such as ngrok or Localtonet." §2.4.1 gives the reason — a
laptop behind NAT is unreachable, and the tunnel performs the traversal.

Two things have to hold at once, and they pull in opposite directions:

* the peer must learn **where** to reach us — a real, public URL;
* the peer must never learn **how** that URL exists — the provider and its authtoken stay
  private, because rule 39 forbids pushing secrets even to a private repository and an ngrok
  token in a negotiated config is exactly that.

The loopback check is the one worth reading. A `127.0.0.1` address is a perfectly valid URL:
negotiation accepts it, both sides sign it, and then the first turn simply never arrives. The
companion repository calls binding `127.0.0.1` "the one-word bug no local test would ever
catch" — so it is caught here, at config time, where the message can still say why.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.shared.private_config import (
    ADDRESS_MEMBERS,
    PrivateConfigError,
    opponent_url,
)
from p2p_thief_agent.shared.tunnel import public_url

TUNNEL = "https://sharnamr-thief.ngrok.io/mcp"


def config(url: str = TUNNEL) -> dict:
    return {"network": {"public_url": url, "opponent_url": "https://rival.ngrok.io/mcp"}}


# --- what the peer is told ------------------------------------------------------------------


def test_the_advertised_address_is_returned() -> None:
    assert public_url(config()) == TUNNEL


def test_the_value_is_stripped_so_a_trailing_newline_does_not_travel() -> None:
    """Tunnel tools print their URL, and a copy-paste carries whitespace. That whitespace
    would end up inside a signed object where both sides must agree byte-for-byte."""
    assert public_url(config(f"  {TUNNEL}\n")) == TUNNEL


@pytest.mark.parametrize("loopback", [
    "http://127.0.0.1:8801/mcp",
    "http://localhost:8801/mcp",
    "http://0.0.0.0:8801/mcp",
    "http://[::1]:8801/mcp",
    "http://127.0.1.1/mcp",
])
def test_a_loopback_address_is_refused(loopback: str) -> None:
    """**The failure this exists to move earlier.** A loopback URL is valid, negotiable and
    signable; it fails at the first turn, by which point both sides have committed to it."""
    with pytest.raises(PrivateConfigError, match="loopback"):
        public_url(config(loopback))


@pytest.mark.parametrize("bad", ["", "   ", "ftp://x/mcp", "sharnamr.ngrok.io/mcp"])
def test_an_unusable_address_is_refused(bad: str) -> None:
    with pytest.raises(PrivateConfigError):
        public_url(config(bad))


def test_a_missing_network_section_is_refused() -> None:
    with pytest.raises(PrivateConfigError, match="network"):
        public_url({})


# --- what the peer is never told --------------------------------------------------------------


def test_every_address_member_is_marked_private() -> None:
    """`M5-005a`. The provider token is not the only leak: a bind host, a port or a tunnel
    URL in a *shared* config would also disclose our deployment. These names may live in the
    private TOML only."""
    for member in ("public_url", "opponent_url", "tunnel_url", "bind_host", "port"):
        assert member in ADDRESS_MEMBERS, f"{member} is not guarded as an address member"


def test_the_provider_is_not_inferable_from_what_is_exchanged() -> None:
    """Only the resulting URL crosses the wire. Whether it came from ngrok, Localtonet or a
    self-hosted domain is a local choice, and nothing in the protocol reveals it `[AE-10]`."""
    for host in ("https://a.ngrok.io/mcp", "https://b.localto.net/mcp", "https://c.example.com/mcp"):
        assert public_url(config(host)) == host


def test_the_two_addresses_are_read_from_different_keys() -> None:
    """Ours and theirs are separate members on purpose: dialling our own advertised address
    would loop a peer back to itself and look exactly like an unresponsive opponent."""
    assert public_url(config()) != opponent_url(config())
