"""Answer "what is armed right now?" in one screen, before a match starts (`M9-038`).

**Why this exists.** Nothing here is a new safety control -- every property it reports is
already enforced structurally somewhere else. What was missing is a way to *see* them. Proving
that email was disabled took four separate greps across two packages; on match day, with an
opponent waiting, "I think it's off" is not a thing anyone should be running on.

**Why it is a readout and not a toggle.** The obvious alternative is an on/off switch for the
reporting layer. A boolean is weaker: it can be defaulted wrong, typo'd, or read from the wrong
file, and it *looks* authoritative while doing none of that. Sending is impossible today
because no credential exists, no CLI verb reaches the sender, and the play path never calls it
-- three structural facts a config key cannot flip. This command reports those facts rather
than adding a fourth thing to trust. (The repositories carried exactly that mistake until
2026-08-08: an `[email] mode = "draft"` key that no code has ever read.)

**The port check is the reference's, and it is here because we have been bitten.** Asked
directly, the reference runs `_ensure_port_free(host, port)` in `infra/mcp_server.py` before
opening anything, because a previous agent still holding the MCP port fails as a bare
`WinError 10048` mid-startup. Our own rehearsals lost runs to stale processes holding a port,
and the failure surfaced as the *opponent* looking absent.

Read-only and offline by design: it binds nothing, sends nothing, and contacts no peer.
"""

from __future__ import annotations

import json
import socket
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from p2p_thief_agent.perception.scent_lock import scent_model_hash
from p2p_thief_agent.protocol.agreement import (
    AgreementError,
    check_appendix_f,
    validate_participants,
)
from p2p_thief_agent.protocol.config_integrity import (
    ConfigIntegrityError,
    check_config_schema_version,
)
from p2p_thief_agent.protocol.terms_projection import terms_from_shared_config
from p2p_thief_agent.services.credential_location import credential_path
from p2p_thief_agent.shared import __version__
from p2p_thief_agent.shared.private_config import load_private_config, opponent_url
from p2p_thief_agent.shared.tunnel import public_url

ARMED = "ARMED"
DISABLED = "DISABLED"


@dataclass(frozen=True)
class Check:
    """One line of the readout. ``ok=None`` is information, not a verdict."""

    name: str
    value: str
    ok: bool | None = None

    @property
    def failed(self) -> bool:
        return self.ok is False


def _identity() -> Check:
    return Check("version", f"code {__version__}")


def _reporting(config: object) -> Check:
    """**The question this command was built to answer.** Absent credential = cannot send.

    Reported as a failure only when a credential *is* present, because for an uncounted
    friendly series an armed sender is the surprising state, not the safe one.
    """
    try:
        path = credential_path(config)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001 - any refusal means no usable credential
        return Check("reporting", f"{DISABLED} ({exc})", ok=None)
    if not path.exists():
        return Check("reporting", f"{DISABLED} (no credential at {path})", ok=None)
    return Check("reporting", f"{ARMED} (credential present at {path})", ok=False)


def _port(config: object) -> Check:
    """Free the port before the opponent needs it (the reference's `_ensure_port_free`)."""
    network = config.get("network", {}) if isinstance(config, dict) else {}
    port = network.get("my_port") if isinstance(network, dict) else None
    if not isinstance(port, int) or port <= 0:
        return Check("port", "no [network].my_port configured", ok=False)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as exc:
            return Check("port", f"{port} IS IN USE — stop the process holding it ({exc})",
                         ok=False)
    return Check("port", f"{port} free", ok=True)


def _wire_gates(game: Mapping[str, object], group_id: object) -> list[Check]:
    """The two refusals the wire applies to a shared file that this readout used to miss.

    Added 2026-08-11 after uoh-ay26 sent a shared file whose `agreed_between` was
    `["cop", "thief"]` -- the two *roles*, not the two group ids -- and whose
    `schema_version` was `"1.00"`. This command printed `ready` for it, because
    `terms_from_shared_config` reads neither field; both refusals only landed
    mid-handshake, with an opponent already waiting. Moving them here is the whole
    point of a preflight.
    """
    checks = []
    try:
        check_config_schema_version(game)
        checks.append(Check("schema version", f"{game.get('schema_version', 'absent')} OK",
                            ok=True))
    except ConfigIntegrityError as exc:
        checks.append(Check("schema version", str(exc), ok=False))
    try:
        validate_participants(game.get("agreed_between"), group_id)
        named = game.get("agreed_between")
        checks.append(Check("participants", f"{' vs '.join(named)} — we are {group_id!r}",  # type: ignore[arg-type]
                            ok=True))
    except AgreementError as exc:
        checks.append(Check("participants", str(exc), ok=False))
    return checks


def _match(path: Path, group_id: object = None) -> list[Check]:
    """Rule 11/12: the shared object must load and satisfy Appendix F before anyone plays."""
    try:
        game = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [Check("match config", f"unreadable: {exc}", ok=False)]
    try:
        terms = terms_from_shared_config(game)
        check_appendix_f(terms)
    except AgreementError as exc:
        return [Check("match config", f"{path.name}: {exc}", ok=False)]
    return [
        Check("match config", f"{path.name} — {len(terms)} terms, Appendix F OK", ok=True),
        *_wire_gates(game, group_id),
        Check("board", f"{terms['board_size']}x{terms['board_size']}, "
                       f"{terms['max_steps']} steps, {terms['barriers_max']} barriers"),
    ]


def preflight(match_path: Path, private_path: Path) -> list[Check]:
    """Every check, in the order an operator reads them. Never raises on a bad input."""
    checks = [_identity()]
    try:
        config = load_private_config(private_path)
    except Exception as exc:  # noqa: BLE001 - report, never crash the readout
        return [*checks, Check("private config", f"{private_path}: {exc}", ok=False)]
    checks.append(Check("private config", f"{private_path.name} loaded", ok=True))
    for label, reader in (("our endpoint", public_url), ("opponent", opponent_url)):
        try:
            checks.append(Check(label, reader(config), ok=True))
        except Exception as exc:  # noqa: BLE001
            checks.append(Check(label, f"missing: {exc}", ok=False))
    checks.append(_port(config))
    game_section = config.get("game", {}) if isinstance(config, dict) else {}
    group_id = game_section.get("group_id") if isinstance(game_section, dict) else None
    checks.extend(_match(match_path, group_id))
    checks.append(Check("scent lock", scent_model_hash()))
    checks.append(_reporting(config))
    return checks
