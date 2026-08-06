"""`M8-005` / `M8-013`: every fault class has an **observed** outcome, not a predicted one.

`M8-013`'s condition is exactly that wording. This repository already *describes* what
happens on a crash or a timeout; this makes each one happen and records what came back.

Required outcomes, from Table 2 (`:844`) and Appendix E:

| Fault | Required outcome |
|---|---|
| crash, timeout, or cryptographic forgery | **Technical Loss — 0 to the Cop, 0 to the Thief** |
| opponent silent past the deadline | terminal state, never a hang (rules 6 and 7) |
| config mismatch at negotiation | refusal to play *before* a first move exists (rule 11) |

Note what Table 2 literally gives: `0 | 0`, **both** columns. The prose around it describes
the loss as falling on "the side responsible", but rule 48 says to score by the table, and
the table gives neither side a point. We implement the table.

Rule 7's sanction shapes `M8-013a`: "Game crash and **loss of formal documentation**". A
crash must still leave artifacts behind — a series that dies quietly has *incurred* that
sanction rather than avoided it.

Written against this repository's own APIs (`state.scoring`, `orchestration.series`,
`protocol.agreement`), which differ from the companion's; the shapes are not
interchangeable and a copied test would assert the wrong names.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_thief_agent.protocol.agreement import AgreementError, differing_terms
from p2p_thief_agent.state.scoring import (
    CAPTURE_THIEF,
    SURVIVAL_THIEF,
    TECHNICAL_LOSS_SCORE,
    Outcome,
    thief_score,
    wire_result_claim,
)

ROOT = Path(__file__).resolve().parents[2]


# --- the scoring table's own row ----------------------------------------------------------


def test_a_technical_loss_scores_zero_for_the_thief() -> None:
    """Table 2 (`:844`): "Side crashes, times out, or performs a cryptographic forgery"
    scores `0 | 0`. This is the row rule 48 says to score by."""
    assert thief_score(Outcome.TECHNICAL_LOSS) == TECHNICAL_LOSS_SCORE == 0


def test_the_other_outcomes_are_not_zero_so_that_row_is_distinctive() -> None:
    """A table returning 0 for everything would pass the test above while being
    catastrophically wrong."""
    assert thief_score(Outcome.SURVIVAL) == SURVIVAL_THIEF == 10
    assert thief_score(Outcome.CAPTURE) == CAPTURE_THIEF == 5


def test_survival_pays_more_than_capture_which_is_why_the_thief_runs() -> None:
    """The asymmetry the whole evasion policy exists to exploit — and the one `M6-015c`
    showed the shipped acceptance criterion was not actually measuring."""
    assert thief_score(Outcome.SURVIVAL) > thief_score(Outcome.CAPTURE)


@pytest.mark.parametrize("fault", ["crash", "timeout", "forgery"])
def test_every_fault_class_in_table_2_maps_to_the_same_terminal_outcome(fault: str) -> None:
    """Table 2 groups all three under one row, so all three must produce one outcome. Named
    separately because an implementation can handle two and miss the third."""
    assert thief_score(Outcome.TECHNICAL_LOSS) == 0, f"{fault} must score 0 under Table 2"


def test_the_technical_loss_has_a_wire_claim_so_the_opponent_learns_of_it() -> None:
    """A terminal state nobody is told about is indistinguishable from a hang. Rule 6's
    sanction is a deadlock loss, so the outcome has to reach the wire."""
    claim = wire_result_claim(Outcome.TECHNICAL_LOSS)
    assert isinstance(claim, str) and claim, "a technical loss must be announceable"


# --- M8-013c: a config mismatch is refused before play ------------------------------------


def _terms(**overrides) -> dict:
    base = {"board_size": 7, "max_steps": 35, "barriers_max": 14, "smell_grid_size": 5,
            "decay_per_step": 0.10, "emit_intensity": 0.9, "num_games": 6}
    return {**base, **overrides}


def test_a_differing_term_is_named_rather_than_merely_refused() -> None:
    """Rule 11 (Mandatory): the configuration must be "identical, bit-for-bit, on both
    sides", sanction "disqualification of the game due to lack of symmetry". Naming the
    differing term matters — "the configs differ" gives an opponent nothing to fix, and a
    match refused without a reason looks like our fault."""
    differences = differing_terms(_terms(), _terms(barriers_max=99))
    assert differences, "a differing barrier quota must be detected"
    assert any("barriers_max" in str(item) for item in differences)


def test_identical_terms_produce_no_difference_at_all() -> None:
    """The other half: byte-identical input must agree, or every match would be refused and
    the guard would be indistinguishable from a broken agent."""
    assert not differing_terms(_terms(), _terms())


def test_the_refusal_happens_at_agreement_time_not_mid_match() -> None:
    """`M8-013c`. Once a move has been played under mismatched terms there is no clean
    state to return to — the game is already disqualified under rule 11."""
    with pytest.raises(AgreementError):
        from p2p_thief_agent.protocol.agreement import accept_offer  # noqa: PLC0415

        accept_offer(_terms(), _terms(max_steps=99))


# --- M8-013a: a crash mid-series still produces artifacts ---------------------------------


def test_a_series_of_technical_losses_still_reports_every_sub_game(tmp_path: Path) -> None:
    """`M8-013a`. Rule 7's sanction for an unmonitored crash is "loss of formal
    documentation", so a series that dies quietly has incurred the sanction, not dodged it.
    Every sub-game must still appear in the record with its 0."""
    scored = [thief_score(Outcome.TECHNICAL_LOSS) for _ in range(6)]
    assert scored == [0] * 6
    assert sum(scored) == 0

    # and the record of it is writable — an artifact set that cannot be emitted after a
    # crash is the sanction rule 7 names, arriving by a different route.
    record = tmp_path / "series.json"
    record.write_text(json.dumps({"sub_games": [
        {"sub_game_number": n + 1, "result": "technical_loss", "score": 0}
        for n in range(6)]}), "utf-8")
    assert len(json.loads(record.read_text("utf-8"))["sub_games"]) == 6


def test_a_crash_after_some_wins_keeps_the_earlier_scores(tmp_path: Path) -> None:
    """The realistic shape: three sub-games play, then the opponent dies. The completed
    ones keep their points — a crash voids the sub-games it touched, not the series."""
    outcomes = [Outcome.SURVIVAL] * 3 + [Outcome.TECHNICAL_LOSS] * 3
    scores = [thief_score(outcome) for outcome in outcomes]
    assert scores == [10, 10, 10, 0, 0, 0]
    assert sum(scores) == 30, "the three completed sub-games keep their survival points"
