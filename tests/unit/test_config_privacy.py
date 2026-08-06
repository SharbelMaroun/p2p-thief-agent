"""`M1-017c`: a shared config carrying a value the book assigns to the private file.

`inst/police_thief_p2p_Summary.md:2901` splits configuration by format precisely here:
"**TOML — For private and local configuration only.** This format is written only in the
private file for each peer — `config/game.toml`: network port, choice of strategy models,
language mode, LLM settings, email, and group identity". `:3001` adds that the private
file is "local and **not subject to negotiation**".

The classes tested below come from that sentence, one refusal per class.
"""

from __future__ import annotations

import pytest

from p2p_thief_agent.protocol.config_integrity import (
    PRIVATE_FIELD_CLASSES,
    ConfigIntegrityError,
    check_no_private_fields,
    private_fields_in,
)

GOOD = {
    "board_size": 7, "smell_grid_size": 5, "decay_per_step": 0.1, "emit_intensity": 0.9,
    "max_steps": 35, "barriers_max": 14, "thief_start": [0, 0], "cop_start": [6, 6],
}


def test_a_clean_shared_config_carries_nothing_private() -> None:
    assert private_fields_in(GOOD) == []
    check_no_private_fields(GOOD)


@pytest.mark.parametrize(
    ("class_name", "key"),
    [
        ("network", "port"),
        ("strategy", "strategy"),
        ("llm", "api_key"),
        ("language", "language_mode"),
        ("contact", "email"),
        ("credential", "credentials"),
    ],
)
def test_one_leakage_vector_per_private_field_class(class_name: str, key: str) -> None:
    """`M1-017c` asks for one vector per class; the classes come from `:2901`, which
    assigns "network port, choice of strategy models, language mode, LLM settings, email,
    and group identity" to the **private** file."""
    assert class_name in PRIVATE_FIELD_CLASSES
    with pytest.raises(ConfigIntegrityError, match=f"{class_name}:{key}"):
        check_no_private_fields({**GOOD, key: "anything"})


def test_the_refusal_names_every_offending_key_not_just_the_first() -> None:
    """A refusal that names one key at a time makes convergence take as many rounds as
    there are mistakes. Rule 11's purpose is that both sides reach one document."""
    with pytest.raises(ConfigIntegrityError) as raised:
        check_no_private_fields({**GOOD, "port": 8000, "email": "a@b.c"})
    assert "network:port" in str(raised.value)
    assert "contact:email" in str(raised.value)


def test_a_suffixed_private_key_is_caught_but_a_legitimate_term_is_not() -> None:
    """`opponent_port` is the same leak wearing a prefix. But `emit_intensity` contains no
    marker and `max_steps` is not `steps`: the guard matches whole keys or `_`-suffixed
    ones, because a substring rule would refuse the agreed parameters it protects."""
    with pytest.raises(ConfigIntegrityError, match="network:opponent_port"):
        check_no_private_fields({**GOOD, "opponent_port": 9000})
    check_no_private_fields({**GOOD, "emit_intensity": 0.9, "max_steps": 35})


def test_the_strategy_selection_is_refused_because_it_is_the_graded_contribution() -> None:
    """Of every class here this is the one that costs marks: the strategy choice is what
    the project is assessed on, and `:3001` puts it in the file "not subject to
    negotiation"."""
    with pytest.raises(ConfigIntegrityError, match="strategy:strategy"):
        check_no_private_fields({**GOOD, "strategy": "belief_pursuit_v2"})
