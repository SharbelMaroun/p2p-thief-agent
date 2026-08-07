"""`M7-013`: the credential's location and its scope are both checked before a report is sent.

Both guards exist because the matching mistake was made on this machine on 2026-08-07, not
because it seemed possible.

A token from another course assignment was offered for reuse. It carried `gmail.modify` and
`calendar` — read, alter and delete on a personal mailbox — and it had a live refresh token,
so it would have sent the report perfectly. Nothing downstream would have complained.

Separately, `.gitignore` covered `token.json` and `credentials.json` but not
`client_secret_<id>.apps.googleusercontent.com.json`, which is the name the Google console
actually downloads. A credential kept inside the tree was therefore one `git add -A` from
being published, and rule 39's sanction is severe security failure and project failure.

No test here writes a real credential. The scope check reads one JSON member, so a fixture
with a `scopes` list and nothing else exercises it exactly as a real token would.
"""

from __future__ import annotations

import json

import pytest

from p2p_thief_agent.services.credential_location import (
    REPOSITORY_ROOT,
    SEND_ONLY,
    assert_send_only,
    credential_path,
)
from p2p_thief_agent.shared.private_config import PrivateConfigError


def token(tmp_path, scopes, name="token.json"):
    path = tmp_path / name
    path.write_text(json.dumps({"scopes": scopes, "refresh_token": "dummy-not-a-token"}),
                    encoding="utf-8")
    return path


# --- where it may live -------------------------------------------------------------------


def test_the_path_comes_from_the_private_config(tmp_path) -> None:
    outside = tmp_path / "secrets" / "token_p2p_send.json"
    config = {"reporting": {"credential_path": str(outside)}}
    assert credential_path(config) == outside


def test_a_path_inside_the_repository_is_refused() -> None:
    """**The first line of defence**, ahead of `.gitignore`. A pattern list protects a file
    only if its name matches; a location rule protects it whatever it is called."""
    inside = REPOSITORY_ROOT / "config" / "token.json"
    with pytest.raises(PrivateConfigError, match="inside the repository"):
        credential_path({"reporting": {"credential_path": str(inside)}})


def test_the_repository_root_itself_is_refused() -> None:
    with pytest.raises(PrivateConfigError, match="inside the repository"):
        credential_path({"reporting": {"credential_path": str(REPOSITORY_ROOT)}})


@pytest.mark.parametrize("config", [
    {},                                            # no section at all
    {"reporting": {}},                             # section, no key
    {"reporting": {"credential_path": "   "}},     # key, no value
    {"reporting": "C:/secrets/token.json"},        # not a table
])
def test_a_missing_or_empty_location_is_refused(config: dict) -> None:
    """Named, not defaulted. Guessing a location is how a report silently goes nowhere, and
    rule 32 makes sending it Mandatory."""
    with pytest.raises(PrivateConfigError):
        credential_path(config)


def test_the_error_points_at_the_runbook() -> None:
    with pytest.raises(PrivateConfigError, match="RUNBOOK"):
        credential_path({"reporting": {}})


# --- what it may do ----------------------------------------------------------------------


def test_a_send_only_token_is_accepted(tmp_path) -> None:
    assert_send_only(token(tmp_path, [SEND_ONLY]))


@pytest.mark.parametrize("scopes", [
    ["https://www.googleapis.com/auth/gmail.modify",
     "https://www.googleapis.com/auth/calendar"],          # the real one found on this machine
    ["https://mail.google.com/"],                          # full mailbox
    ["https://www.googleapis.com/auth/gmail.readonly"],
    [SEND_ONLY, "https://www.googleapis.com/auth/calendar"],   # send-only PLUS extra
    [],
])
def test_anything_broader_than_sending_is_refused(tmp_path, scopes: list) -> None:
    """`[SEND_ONLY, extra]` is in the list deliberately: "contains send" is the check a
    reasonable person writes, and it would pass a token that also reads the mailbox."""
    with pytest.raises(PrivateConfigError, match="send-only|scopes"):
        assert_send_only(token(tmp_path, scopes))


def test_a_token_without_a_scopes_member_is_refused(tmp_path) -> None:
    """Unknown is not the same as fine. If what it permits cannot be read, it is not used."""
    path = tmp_path / "token.json"
    path.write_text(json.dumps({"refresh_token": "dummy-not-a-token"}), encoding="utf-8")
    with pytest.raises(PrivateConfigError, match="no scopes"):
        assert_send_only(path)


def test_an_unreadable_or_malformed_token_is_refused(tmp_path) -> None:
    (tmp_path / "bad.json").write_text("not json at all", encoding="utf-8")
    with pytest.raises(PrivateConfigError, match="readable JSON"):
        assert_send_only(tmp_path / "bad.json")
    with pytest.raises(PrivateConfigError, match="cannot read"):
        assert_send_only(tmp_path / "absent.json")


def test_the_scope_check_reads_nothing_but_scopes(tmp_path, capsys) -> None:
    """The guard must not become a way to spill a token. Nothing is printed, and the
    function returns None rather than handing the caller the credential."""
    assert assert_send_only(token(tmp_path, [SEND_ONLY])) is None
    assert capsys.readouterr().out == ""
