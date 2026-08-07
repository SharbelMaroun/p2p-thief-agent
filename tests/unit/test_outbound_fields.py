"""`M8-009b`: a leakage vector per private field class, per channel.

The row's condition is literally "leakage vector per private field class", so there is one
test per class. Rule 2 (Prohibited) sanctions data leakage with **immediate
disqualification**, which is why the guard raises rather than stripping: silently
sanitising hides the bug that put the field there.

The harder half is the *permitted* disclosures. `llm_model` and `mcp_servers` are private
under `:2901` and yet **mandatory** in the declaration — running this repository's existing
`check_no_private_fields` over a legitimate declaration group refuses it. A boundary is
only correct if it also lets the legal case through, so that is tested too.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.protocol.config_integrity import (
    PRIVATE_FIELD_CLASSES,
    check_no_private_fields,
)
from p2p_thief_agent.protocol.outbound_fields import (
    CHANNEL_DISCLOSURES,
    OutboundLeakError,
    check_outbound,
    outbound_leaks,
)

# A key-SHAPED value that is not a key. Named with a marker the secret scanner already
# recognises as a placeholder, because the scanner is right to flag a credential-looking
# literal next to `api_key` and silencing it with an allowlist entry would weaken it for
# every future file.
PLACEHOLDER_KEY = "sk-placeholder-" + "0" * 12
PLACEHOLDER_TOKEN = "placeholder-refresh-token"

VECTORS = {
    "network": {"my_port": 8802},
    "strategy": {"thief_class": "EvasiveBelief", "seed": 4321},
    "llm": {"provider": "ollama", "api_key": PLACEHOLDER_KEY},
    "language": {"banter": True},
    "contact": {"recipient": "someone@example.com"},
    "credential": {"refresh_token": PLACEHOLDER_TOKEN},
}


@pytest.mark.parametrize("field_class", sorted(PRIVATE_FIELD_CLASSES))
def test_each_private_field_class_is_caught_in_the_shared_config(field_class: str) -> None:
    """**The row's own condition.** Rule 11 makes the signed terms byte-identical on both
    sides, so a private value here is our local truth inside a document they also sign."""
    leaks = outbound_leaks(VECTORS[field_class], "shared_config")
    assert leaks, f"no vector detected for the {field_class} class"
    assert all(leak.startswith(f"{field_class}:") for leak in leaks), leaks


@pytest.mark.parametrize("field_class", sorted(PRIVATE_FIELD_CLASSES))
def test_each_private_field_class_is_caught_in_a_turn_message(field_class: str) -> None:
    """A turn carries a digest, then a move and a hint. A turn also crosses the wire far
    more often than a config, so it is the cheaper place for something to ride along."""
    turn = {"step": 3, "sender": "thief", "commit": "a" * 64, **VECTORS[field_class]}
    assert outbound_leaks(turn, "turn"), f"{field_class} rode a turn message unnoticed"


def test_a_leak_nested_several_levels_deep_is_found() -> None:
    """The realistic shape: an API key arrives inside an identity block inside a payload,
    never at the top level where anyone would notice it."""
    document = {"payload": {"identity": {"settings": {"api_key": PLACEHOLDER_KEY}}}}
    assert outbound_leaks(document, "shared_config")


def test_a_leak_inside_a_list_element_is_found() -> None:
    """Groups arrive as a list, so a per-group leak sits in a list position."""
    document = {"groups": [{"group_id": "a"}, {"group_id": "b", "thief_class": "X"}]}
    assert outbound_leaks(document, "shared_config")


# --- the permitted disclosures ------------------------------------------------------------


def test_the_declaration_may_carry_the_model_name_and_the_mcp_urls() -> None:
    """Required by rule 24 and `:2229`. This is the case the existing single-channel guard
    gets wrong, which is why the channel dimension exists at all."""
    group = {"group_id": "sharNamr", "llm_model": "template",
             "mcp_servers": {"peer": "https://x.example.com/mcp"}}
    check_outbound({"groups": [group]}, "declaration")


def test_the_existing_single_channel_guard_still_refuses_that_same_group() -> None:
    """**The contrast that motivated this module.** `check_no_private_fields` is correct for
    the shared config and wrong for the declaration; both statements are pinned here so
    neither guard gets "fixed" into agreeing with the other."""
    group = {"group_id": "sharNamr", "llm_model": "template"}
    check_outbound({"groups": [group]}, "declaration")
    with pytest.raises(Exception, match="private"):
        check_no_private_fields(group)


def test_the_declaration_still_refuses_the_provider_behind_the_model() -> None:
    """The fine distinction worth keeping: the declaration says **which model**, never
    **how we reach it**."""
    with pytest.raises(OutboundLeakError, match="llm:"):
        check_outbound({"llm_model": "haiku", "provider": "ollama"}, "declaration")


def test_an_mcp_url_containing_a_port_is_not_flagged_as_a_port_leak() -> None:
    """Keys, not values. The mandatory URL contains a port by construction."""
    check_outbound({"mcp_servers": {"peer": "http://127.0.0.1:8802/mcp"}}, "declaration")


# --- the guard's own failure modes ---------------------------------------------------------


def test_an_unknown_channel_is_refused_rather_than_defaulted() -> None:
    with pytest.raises(OutboundLeakError, match="unknown channel"):
        outbound_leaks({"anything": 1}, "gossip")


def test_a_clean_document_passes_every_channel() -> None:
    """A guard that refused everything would pass every leak test and block every match."""
    clean = {"step": 1, "sender": "thief", "commit": "a" * 64, "hint": "past the market"}
    for channel in CHANNEL_DISCLOSURES:
        check_outbound(clean, channel)


def test_the_error_names_the_class_and_the_path() -> None:
    """An operator needs to know what kind of thing escaped and where it sat."""
    with pytest.raises(OutboundLeakError) as caught:
        check_outbound({"identity": {"seed": 7}}, "turn")
    assert "strategy:identity.seed" in str(caught.value) and "AE-2" in str(caught.value)


def test_the_merged_class_list_keeps_every_key_the_original_guard_knew() -> None:
    """This module extends `config_integrity`'s classes rather than restating them. Two
    lists of private keys would drift, and the drift would stay silent until a match was
    already disqualified."""
    for name, keys in PRIVATE_FIELD_CLASSES.items():
        for key in keys:
            assert outbound_leaks({key: "x"}, "shared_config"), f"{name}:{key} was dropped"
