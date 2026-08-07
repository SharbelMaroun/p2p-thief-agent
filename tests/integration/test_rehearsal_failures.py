"""`M7-018a`: a technical loss still produces a complete artifact set.

This is the rehearsal that matters most, and the one a happy-path run never exercises. The
game that goes wrong is the game whose evidence gets disputed — a technical loss under rule
19, a capture, a disconnection — and a pipeline that only emits artifacts when things went
well destroys exactly the record an auditor needs.

So every assertion below is of the form *the bad outcome changed the numbers and nothing
else*. Four artifact families, one shared `game_uid`, every config committed, the audit
still run, the result still agreed and sent. The loss is visible in the score, not in what
is missing.
"""

from __future__ import annotations

import json

import pytest

from p2p_thief_agent.orchestration.series import THIEF_SUBGAMES_NATURAL
from p2p_thief_agent.reporting.retention import missing_configs
from p2p_thief_agent.state.scoring import Outcome
from tests.integration.rehearsal import rehearse, shared_uid

LOST = THIEF_SUBGAMES_NATURAL[1]


@pytest.fixture(scope="module")
def clean(tmp_path_factory):
    return rehearse(tmp_path_factory.mktemp("baseline"))


@pytest.fixture(scope="module")
def with_loss(tmp_path_factory):
    """One sub-game lost on a technical forfeit — rule 19's sanction, not a played defeat."""
    return rehearse(tmp_path_factory.mktemp("loss"),
                    outcomes={LOST: Outcome.TECHNICAL_LOSS})


def test_the_lost_series_still_produces_all_four_artifact_families(with_loss) -> None:
    kinds = {name.split("_", 1)[0] for name in with_loss.artifacts}
    assert kinds == {"declaration", "config", "log", "result"}


def test_the_lost_series_produces_exactly_as_many_files_as_a_clean_one(clean, with_loss) -> None:
    """**The claim in its strongest form.** Not "artifacts exist" but "the same artifacts
    exist" — a pipeline that drops one file per bad sub-game passes a weaker assertion."""
    assert sorted(with_loss.artifacts) == sorted(clean.artifacts)
    assert len(with_loss.written) == len(clean.written)


def test_every_artifact_of_the_lost_series_still_shares_one_game_uid(with_loss) -> None:
    assert shared_uid(with_loss) == with_loss.identity.game_uid


def test_every_config_is_still_committed(with_loss) -> None:
    """Appendix F obligation 4 makes no exception for a game that went badly, and the badly
    gone game is the one somebody will want to reproduce."""
    root = with_loss.written[next(iter(with_loss.written))].parent.parent
    assert missing_configs(root, with_loss.identity.game_id, THIEF_SUBGAMES_NATURAL) == ()


def test_the_loss_shows_up_in_the_score_rather_than_in_a_missing_file(clean, with_loss) -> None:
    assert with_loss.series_score < clean.series_score


def test_the_result_records_the_technical_loss_by_name(with_loss) -> None:
    """Named, not merely scored as zero. Rule 19's technical loss and a played defeat carry
    different sanctions, and a result that only reports points cannot tell them apart."""
    result = next(body for name, body in with_loss.artifacts.items()
                  if name.startswith("result_"))
    lost_line = next(line for line in result["sub_games"] if line["sub_game_number"] == LOST)
    assert lost_line["result"] == Outcome.TECHNICAL_LOSS.value
    assert lost_line["winner_group"] != "sharNamr"


def test_the_lost_sub_game_still_has_its_own_log_with_records(with_loss) -> None:
    """The log of the sub-game that was forfeited is the evidence of *why*, so it is the
    last thing that should be thin."""
    log = next(body for name, body in with_loss.artifacts.items()
               if name.startswith("log_") and f"g{LOST:02d}" in name)
    assert log["records"], "the forfeited sub-game produced an empty log"
    assert all(entry["commit"] and entry["nonce"] for entry in log["records"])


def test_the_audit_and_agreement_still_ran_after_a_loss(with_loss) -> None:
    """A loss is not a falsification. Rule 19 punishes a technical *mismatch*; losing a
    sub-game honestly leaves the audit passing and the result agreeable."""
    assert with_loss.settlement["audit_passed"] is True
    assert with_loss.settlement["state"] == "agreed"


def test_the_report_is_still_sent_after_a_loss(with_loss) -> None:
    """Rule 32 makes reporting Mandatory and does not condition it on winning; a side that
    does not send scores nothing whatever happened in the game."""
    assert len(with_loss.transport.sent) == 1


def test_every_written_artifact_of_the_lost_series_reads_back(with_loss) -> None:
    for path in with_loss.written.values():
        assert json.loads(path.read_text(encoding="utf-8"))


def test_the_token_ledger_still_accounts_for_the_lost_sub_game(with_loss) -> None:
    """A forfeited sub-game still spent tokens, and rule 54 asks what was spent rather than
    what was spent usefully."""
    assert LOST in with_loss.tokens["per_sub_game"]
    assert with_loss.tokens["per_sub_game"][LOST] > 0
