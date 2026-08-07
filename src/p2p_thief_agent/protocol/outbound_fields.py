"""What may leave this process, per channel (`M8-009b`).

`config_integrity.check_no_private_fields` already answers this for **one** channel: the
shared signed config, where the answer is "none". This module is the rest of the question,
and it exists because the one-channel answer turns out to be wrong for every other channel.

Rule 2 (Prohibited): "Do not share memory or variables between parties at all. Sanction:
**Immediate disqualification due to data leakage**." `:2897` draws the line — "everything
that both sides must agree upon is written in JSON; everything that is private and local is
written in TOML" — and `:2901` names it: "network port, choice of strategy models, language
mode, LLM settings, email, and group identity".

**The same key is forbidden in one document and mandatory in another.** Running the existing
guard over a legitimate declaration group refuses it:

    private fields found in a legitimate declaration group: ['llm:llm_model']
    -> guard REFUSES it

But `llm_model` is **required** there — asked directly, the declaration must disclose
`group_id`, `group_name`, `members`, `repos`, `mcp_servers`, `llm_model`, the hardware spec
and a `signature`. `reporting/declaration.py` lists it among the required group keys, so a
blanket guard would break a mandatory artifact.

So each channel declares what it must disclose. What stays private everywhere, confirmed
against the reference: the LLM **provider** (as distinct from the model name), the RNG seed,
the strategy selector, any API key, the reporting email, and internal deadlines. The
declaration says *which model*, never *how we reach it*.

**Keys, not values.** A required `mcp_servers` URL contains a port by construction, so a
value-matching guard would refuse the mandatory disclosure.
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_thief_agent.protocol.config_integrity import PRIVATE_FIELD_CLASSES

# Reuses `config_integrity`'s classes rather than restating them: two lists of private keys
# would drift, and the drift would be silent until a match was already disqualified.
EXTRA_PRIVATE = {
    "network": ("my_port", "mcp_servers", "hostname", "tunnel"),
    "strategy": ("thief_class", "police_class", "rng_seed"),
    "llm": ("llm_provider", "anthropic_api_key", "step_deadline_seconds"),
    "contact": ("recipient",),
    "credential": ("client_secret", "refresh_token"),
}

CHANNEL_DISCLOSURES: dict[str, frozenset[str]] = {
    "shared_config": frozenset(),
    "declaration": frozenset({"llm_model", "mcp_servers"}),
    "turn": frozenset(),
    "audit": frozenset(),
    "result": frozenset(),
}


class OutboundLeakError(ValueError):
    """Raised when a document would carry a private field out of this process."""


def _classes() -> dict[str, tuple[str, ...]]:
    merged = {name: tuple(keys) for name, keys in PRIVATE_FIELD_CLASSES.items()}
    for name, extra in EXTRA_PRIVATE.items():
        merged[name] = tuple(dict.fromkeys(merged.get(name, ()) + extra))
    return merged


def _walk(node: object, path: str = "") -> list[tuple[str, str]]:
    """Every (key, path) pair in a nested document — a leak three levels down is the
    realistic one, because nobody puts an API key at the top of a message."""
    found: list[tuple[str, str]] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            found.append((str(key), here))
            found.extend(_walk(value, here))
    elif isinstance(node, (list, tuple)) and not isinstance(node, (str, bytes)):
        for index, value in enumerate(node):
            found.extend(_walk(value, f"{path}[{index}]"))
    return found


def outbound_leaks(document: object, channel: str) -> list[str]:
    """Return `class:path` for every private field this channel may not disclose.

    An unknown channel is refused rather than defaulted. Defaulting permissive ships a new
    message type unguarded; defaulting strict silently drops a mandatory field. Refusing
    forces the new channel to state what it discloses.
    """
    if channel not in CHANNEL_DISCLOSURES:
        raise OutboundLeakError(
            f"unknown channel {channel!r}; declare its disclosures in CHANNEL_DISCLOSURES")
    allowed = CHANNEL_DISCLOSURES[channel]
    classes = _classes()
    leaks: list[str] = []
    for key, path in _walk(document):
        lowered = key.lower()
        if lowered in allowed:
            continue
        for name, members in classes.items():
            if lowered in members:
                leaks.append(f"{name}:{path}")
                break
    return sorted(set(leaks))


def check_outbound(document: object, channel: str) -> None:
    """Refuse to send a document carrying a private field.

    Raises rather than stripping. Rule 2's sanction is immediate disqualification, and
    silently sanitising would hide the bug that put the field there — shipping the next one.
    """
    leaks = outbound_leaks(document, channel)
    if leaks:
        raise OutboundLeakError(
            f"{channel} would carry private field(s) {', '.join(leaks)}; rule 2 sanctions "
            "data leakage with immediate disqualification [AE-2], and `:2901` keeps these "
            "in the private TOML")
