"""Drive a full local series rehearsal from the real pieces (`M7-018`).

The rehearsal answers a specific question: *if we ran a counted game right now, would
anything be missing?* Every unit test in this repository proves one component behaves; none
proves the components connect. The failures this catches live at the seams — an artifact that
validates alone but shares no `game_uid` with its siblings, a settlement that never reaches
the composer, a config written where `.gitignore` swallows it.

Nothing is mocked except the transport. The builders, audit, settlement, ledgers and
retention store are the ones that will play the counted game; a rehearsal against test
doubles would rehearse the doubles.

Used by `test_rehearsal.py` (`M7-018`), `test_rehearsal_failures.py` (`M7-018a`, a
deliberately lost sub-game) and `test_rehearsal_tampering.py` (`M7-018b`, a forged audit).
"""

from __future__ import annotations

from pathlib import Path

from p2p_thief_agent.orchestration.series import THIEF_SUBGAMES_NATURAL, run_thief_series
from p2p_thief_agent.orchestration.settlement import agree, audit_series, settlement_record
from p2p_thief_agent.reporting.artifact_schema import check_shared_game_uid, validate_artifact
from p2p_thief_agent.reporting.config_artifact import build_config
from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.email_report import compose_report
from p2p_thief_agent.reporting.emit import write_all
from p2p_thief_agent.reporting.gmail_wire import api_send
from p2p_thief_agent.reporting.log_artifact import build_log
from p2p_thief_agent.reporting.naming import MatchIdentity, match_filenames
from p2p_thief_agent.reporting.result_artifact import build_result
from p2p_thief_agent.reporting.retention import missing_configs, store_config
from p2p_thief_agent.reporting.token_ledger import TokenLedger, TokenUsage
from p2p_thief_agent.state.scoring import Outcome
from tests.integration.rehearsal_fixtures import (
    COMMIT_HASH,
    OPPONENT,
    OUR_GROUP,
    SECTIONS,
    TOKEN_LIMIT,
    RecordingTransport,
    Rehearsal,
    group,
    steps_for,
    summary_for,
)

__all__ = ["OPPONENT", "OUR_GROUP", "TOKEN_LIMIT", "Rehearsal", "rehearse", "shared_uid"]


def rehearse(
    root: Path,
    *,
    outcomes: dict[int, Outcome] | None = None,
    tamper_sub_game: int | None = None,
) -> Rehearsal:
    """Play a whole series locally and produce everything a counted game would.

    `outcomes` overrides individual sub-game results (`M7-018a`); `tamper_sub_game` forges
    one revealed move after its commitment was taken (`M7-018b`). Both default to the clean
    path, so a test asks for exactly the damage it wants to observe.
    """
    outcomes = outcomes or {}
    identity = MatchIdentity(game_id=f"{OUR_GROUP}-vs-{OPPONENT}", game_uid="r" * 32)
    groups = [group(OUR_GROUP), group(OPPONENT)]
    names = match_filenames(identity, THIEF_SUBGAMES_NATURAL)
    ledger = TokenLedger(max_tokens_per_game=TOKEN_LIMIT)

    def play(number: int) -> Outcome:
        ledger.record(number, TokenUsage(prompt=8_000 + number, completion=4_000))
        return outcomes.get(number, Outcome.SURVIVAL)

    series = run_thief_series(identity.game_id, THIEF_SUBGAMES_NATURAL, play)

    reveals = [{"sub_game": line.sub_game_number,
                "records": steps_for(line.sub_game_number,
                                     tamper=line.sub_game_number == tamper_sub_game)}
               for line in series.sub_games]
    audit = audit_series(reveals)
    settled = agree(audit, ours=series.cumulative_score,
                    theirs=series.cumulative_score if audit.passed else None)
    record = settlement_record(settled)

    artifacts: dict[str, dict] = {
        names["declaration"]: build_declaration(
            identity=identity, groups=groups, num_sub_games=len(THIEF_SUBGAMES_NATURAL),
            max_tokens_per_game=TOKEN_LIMIT, timezone="Asia/Jerusalem",
            started_at="2026-08-07T10:00:00+03:00", ended_at="2026-08-07T13:00:00+03:00",
            links={}, github_commit=COMMIT_HASH),
    }
    for index, line in enumerate(series.sub_games):
        number = line.sub_game_number
        config = build_config(identity=identity, sub_game_number=number,
                              agreed_between=[OUR_GROUP, OPPONENT], sections=SECTIONS,
                              links={}, config_name=names["configs"][index])
        artifacts[names["configs"][index]] = config
        store_config(root, identity, number, config)
        artifacts[names["logs"][index]] = build_log(
            identity=identity, summary=summary_for(number, line.outcome, ledger.tokens_for(number)),
            links={}, mutual_agreement={**record, "opponent_group_id": OPPONENT,
                                        "sha256": "f" * 64, "confirmed": settled.reportable},
            records=reveals[index]["records"])

    sub_lines = [{"sub_game_number": line.sub_game_number, "roles": {"thief": OUR_GROUP},
                  "started_at": "t0", "ended_at": "t1", "result": line.outcome.value,
                  "winner_group": OUR_GROUP if line.score > 0 else OPPONENT,
                  "tie": line.outcome is Outcome.TIE, "github_commit": COMMIT_HASH,
                  "tokens": ledger.tokens_for(line.sub_game_number), "score": line.score,
                  "log_files": [], "audit": {"passed": audit.passed}}
                 for line in series.sub_games]
    artifacts[names["result"]] = build_result(
        identity=identity, groups=groups, sub_games=sub_lines,
        final_result={"total_score": series.cumulative_score,
                      "sub_games_won": sum(1 for line in series.sub_games if line.score > 0),
                      "ties": sum(1 for line in series.sub_games if line.outcome is Outcome.TIE),
                      "winner_group": OUR_GROUP, "series_tie": False,
                      "tokens_total_series": ledger.tokens_total_series},
        timezone="Asia/Jerusalem",
        mutual_agreement={**record, "opponent_group_id": OPPONENT, "sha256": "f" * 64,
                          "confirmed": settled.reportable})

    for filename, artifact in artifacts.items():
        validate_artifact(filename.split("_", 1)[0], artifact)
    written = write_all(root / "rehearsal-output", artifacts)

    transport = RecordingTransport()
    if settled.reportable:
        api_send(transport, compose_report(
            result=artifacts[names["result"]], settlement=record, sender="thief@example.com",
            game_id=identity.game_id, team_code="sharNamr"))

    assert missing_configs(root, identity.game_id, THIEF_SUBGAMES_NATURAL) == ()
    return Rehearsal(identity=identity, artifacts=artifacts, written=written,
                     settlement=record, tokens=ledger.report(),
                     series_score=series.cumulative_score, transport=transport)


def shared_uid(rehearsal: Rehearsal) -> str:
    """Regroup the written artifacts by kind so the whole set can be uid-checked."""
    by_kind = {name.split("_", 1)[0]: body for name, body in rehearsal.artifacts.items()}
    return check_shared_game_uid(by_kind)
