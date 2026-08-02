"""Thief-private local configuration: where the opponent's address lives (`M5-002f`).

Configuration is split in two and the split is load-bearing. The **shared** match
JSON is the constitution both peers sign and hash, so it must be byte-identical on
both sides. The **private** `config/game.toml` is this peer's own business -- its
port, the opponent's URL, its model choice, its credentials -- and is never
negotiated, never signed, and never sent.

Confirmed against the pinned simulator wire reference on 2026-07-31 (`THIEF-002`:
its wire behaviour is matched, its source is never copied). Each peer reads its own
`config/<role>/game.toml`, police and thief from **separate directories**, and takes
the opponent's address from the `[network]` section under `opponent_url`. Asked
directly whether the shared negotiated JSON ever carries a URL, port, host, or any
network address, the answer was a flat no: local settings must not "leak into the
agreement". The book publishes the same skeleton on page 131, and the reference's
`[network]` section carries `my_port`, `opponent_url`, `turn_timeout_seconds`,
`poll_interval_seconds`, `connect_timeout_seconds`, `retry_interval_seconds`, and
`audit_send_timeout_seconds`.

`ADR-0004` left the exact private keys `PENDING`; this closes them. The module is the
only way in to an opponent address, and `assert_no_network_address` guards the way
out: a shared object carrying one is refused before it can be signed `[AE-10]`
`[AE-39]`.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path

import tomllib

NETWORK_SECTION = "network"
OPPONENT_URL_KEY = "opponent_url"
DIALABLE_SCHEMES = ("http://", "https://")

# This peer runs under its own role directory, never the opponent's (`M5-006`).
# The book and the pinned reference both split private config as `config/<role>/`,
# so two peers on one machine cannot cross-read each other's ports, URLs, or model
# choice. Reading is scoped to `thief/` by construction, not by convention `[AE-1]`.
THIEF_ROLE = "thief"
PRIVATE_CONFIG_NAME = "game.toml"

# Member names that name a network address, and so belong only in private TOML.
ADDRESS_MEMBERS = frozenset(
    {
        "address",
        "bind_host",
        "bind_port",
        "endpoint",
        "host",
        "hostname",
        "mcp_servers",
        "my_port",
        "opponent_url",
        "port",
        "public_url",
        "tunnel_url",
        "url",
    }
)


class PrivateConfigError(ValueError):
    """Raised when private configuration is absent, malformed, or unusable."""


class SharedConfigLeakError(ValueError):
    """Raised when a shared match object carries a private network address."""


def load_private_config(path: str | Path) -> dict:
    """Parse one explicit private TOML path; nothing is guessed or searched for."""
    source = Path(path)
    try:
        with source.open("rb") as handle:
            return tomllib.load(handle)
    except OSError as exc:
        raise PrivateConfigError(f"cannot read private config {source}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise PrivateConfigError(f"private config {source} is not valid TOML: {exc}") from exc


def opponent_url(config: Mapping) -> str:
    """Return `[network].opponent_url` -- the one address this peer may dial."""
    section = config.get(NETWORK_SECTION)
    if not isinstance(section, Mapping):
        raise PrivateConfigError(f"private config has no [{NETWORK_SECTION}] section")
    value = section.get(OPPONENT_URL_KEY)
    if not isinstance(value, str) or not value.strip():
        raise PrivateConfigError(f"[{NETWORK_SECTION}].{OPPONENT_URL_KEY} must be a non-empty string")
    url = value.strip()
    if not url.startswith(DIALABLE_SCHEMES):
        raise PrivateConfigError(f"[{NETWORK_SECTION}].{OPPONENT_URL_KEY} must be http(s), got {url!r}")
    return url


def load_opponent_url(path: str | Path) -> str:
    """Read the opponent's address from one explicit private TOML path."""
    return opponent_url(load_private_config(path))


def thief_config_path(config_root: str | Path) -> Path:
    """Return this peer's own private-config path: `<config_root>/thief/game.toml`.

    Role-scoped by construction (`M5-006`): the Thief resolves only its own
    directory, so it can never read the police peer's private settings even when
    both run from one checkout `[AE-1]` `[AE-2]`.
    """
    return Path(config_root) / THIEF_ROLE / PRIVATE_CONFIG_NAME


def load_thief_private_config(config_root: str | Path) -> dict:
    """Load the Thief's private TOML from its own `config/thief/` directory."""
    return load_private_config(thief_config_path(config_root))


def assert_no_network_address(shared: Mapping) -> None:
    """Refuse a shared match object that carries any network address.

    Two checks, because either on its own is easy to slip past: a member *named*
    like an address, and any string value that *is* one. Timeouts and league counts
    are legitimate shared terms, so the check is about addresses, not about the
    word "network".
    """
    for trail, name, value in _members(shared):
        if name.lower() in ADDRESS_MEMBERS:
            raise SharedConfigLeakError(
                f"shared match object carries private network member {trail!r}; "
                f"an address belongs only in config/game.toml [{NETWORK_SECTION}]"
            )
        if isinstance(value, str) and "://" in value:
            raise SharedConfigLeakError(
                f"shared match object carries a network address at {trail!r}: {value!r}"
            )


def _members(node: object, trail: str = "") -> Iterator[tuple[str, str, object]]:
    """Walk a decoded JSON tree, yielding (dotted path, member name, value)."""
    if isinstance(node, Mapping):
        for key, value in node.items():
            here = f"{trail}.{key}" if trail else str(key)
            yield here, str(key), value
            yield from _members(value, here)
    elif isinstance(node, Sequence) and not isinstance(node, str | bytes):
        for index, value in enumerate(node):
            here = f"{trail}[{index}]"
            yield here, "", value
            yield from _members(value, here)
