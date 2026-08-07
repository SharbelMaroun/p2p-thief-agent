"""`M7-023`, behaviourally: the whole artifact set is produced with the peer gone.

`test_transport_independence.py` proves nothing under `reporting/` imports the transport
layer. This proves the consequence that matters — a game abandoned because the opponent
vanished still writes its four files.

That is the realistic case, not an edge one. The game whose evidence gets disputed is
exactly the game that went wrong, so `confirmed: False` runs through every fixture here.
A pipeline that refuses to record an unconfirmed outcome destroys the evidence rule 35
exists to settle.
"""

from __future__ import annotations

from p2p_thief_agent.reporting.config_artifact import build_config
from p2p_thief_agent.reporting.declaration import build_declaration
from p2p_thief_agent.reporting.emit import artifact_bytes, write_all
from p2p_thief_agent.reporting.log_artifact import build_log
from p2p_thief_agent.reporting.naming import MatchIdentity, match_filenames
from p2p_thief_agent.reporting.result_artifact import build_result

ID = MatchIdentity(game_id="disconnected", game_uid="d" * 32)
COMMIT = "a" * 40
HARDWARE = {"cpu_type": "x86_64", "cpu_freq_mhz": 3000, "cpu_cores": 8,
            "ram_gb": 16, "gpu_model": "none", "vram_gb": 0}
AGREEMENT = {"confirmed": False, "opponent_group_id": "vanished", "sha256": "f" * 64}
SECTIONS = {name: {"k": 1} for name in
            ("board_and_agents", "world", "movement_and_barriers", "scoring", "pheromones",
             "network_and_league", "rate_limiter_gatekeeper")}
SUMMARY = {**dict.fromkeys(
    ("sub_game_number", "group_id", "role", "opponent_group_id", "result", "winner_role",
     "steps", "timezone", "started_at", "duration_seconds", "tokens_total", "audit"), 0),
    "ended_at": "2026-08-07T12:00:00+03:00"}
SUB_GAME = {"sub_game_number": 1, "roles": {}, "started_at": "t0", "ended_at": "t1",
            "result": "abandoned", "winner_group": "", "tie": False,
            "github_commit": COMMIT, "tokens": 0, "score": 0, "log_files": [], "audit": {}}
FINAL = {"total_score": 0, "sub_games_won": 0, "ties": 0, "winner_group": "",
         "series_tie": False, "tokens_total_series": 0}
RECORD = {"payload": {"step": 1}, "nonce": "n" * 32, "commit": "c" * 64}


def group(gid: str) -> dict:
    return {"group_id": gid, "group_name": gid, "members": ["student-1"],
            "repos": {"cop": f"https://github.com/{gid}/cop",
                      "thief": f"https://github.com/{gid}/thief"},
            "mcp_servers": {"peer": f"https://{gid}.example.com/mcp"},
            "llm_model": "template-free", "hardware_spec": HARDWARE, "signature": "sig"}


GROUPS = [group("sharNamr"), group("vanished")]


def abandoned_set() -> dict[str, dict]:
    """Every artifact of a game the opponent walked out of."""
    names = match_filenames(ID, [1])
    return {
        names["declaration"]: build_declaration(
            identity=ID, groups=GROUPS, num_sub_games=6, max_tokens_per_game=200_000,
            timezone="UTC", started_at="t0", ended_at="t1", links={}, github_commit=COMMIT),
        names["configs"][0]: build_config(
            identity=ID, sub_game_number=1, agreed_between=["sharNamr", "vanished"],
            sections=SECTIONS, links={}, config_name=names["configs"][0]),
        names["logs"][0]: build_log(
            identity=ID, summary=SUMMARY, links={}, mutual_agreement=AGREEMENT,
            records=[RECORD]),
        names["result"]: build_result(
            identity=ID, groups=GROUPS, sub_games=[SUB_GAME], final_result=FINAL,
            timezone="UTC", mutual_agreement=AGREEMENT),
    }


def test_the_full_artifact_set_is_built_and_written_with_no_peer(tmp_path) -> None:
    written = write_all(tmp_path, abandoned_set())
    assert len(written) == 4
    assert all(path.is_file() and path.stat().st_size > 0 for path in written.values())


def test_an_unconfirmed_mutual_agreement_still_produces_a_log() -> None:
    """A log is refused for having no records or no end time — never for the opponent
    having failed to confirm. Refusing here destroys the evidence of exactly the dispute
    rule 35 exists to settle."""
    artifact = build_log(identity=ID, summary=SUMMARY, links={}, mutual_agreement=AGREEMENT,
                         records=[RECORD])
    assert artifact["mutual_agreement"]["confirmed"] is False


def test_the_abandoned_result_records_a_zero_score_rather_than_no_result() -> None:
    """A game that ended badly and a game that never happened are different claims, and
    only the first can be audited."""
    result = abandoned_set()["result_disconnected.json"]
    assert result["final_result"]["total_score"] == 0
    assert result["sub_games"][0]["result"] == "abandoned"


def test_serialization_needs_nothing_from_the_transport(monkeypatch) -> None:
    """`socket.socket` replaced by something that raises on contact, so a transport call
    inside serialization surfaces here rather than as a timeout during a game."""
    import socket  # noqa: PLC0415

    def refuse(*_args, **_kwargs):
        raise AssertionError("artifact emission opened a socket")

    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    assert artifact_bytes({"_schema": "result", "game_uid": ID.game_uid}).endswith(b"\n")


def test_the_whole_set_writes_with_the_socket_module_disabled(tmp_path, monkeypatch) -> None:
    """The end-to-end form of the claim: build **and** write four artifacts while any
    attempt to open a connection raises."""
    import socket  # noqa: PLC0415

    def refuse(*_args, **_kwargs):
        raise AssertionError("artifact emission opened a socket")

    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    assert len(write_all(tmp_path, abandoned_set())) == 4
