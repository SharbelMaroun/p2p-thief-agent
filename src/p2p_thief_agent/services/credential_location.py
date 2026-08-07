"""Where the Gmail credential lives, and what it is allowed to be (`M7-013`).

The send path takes `credential_path` as an argument so the secret never has to sit beside
the code. Nothing supplied that argument in production until now: the consent flow was run by
hand and the location lived in someone's head.

Two guards, and both exist because the corresponding mistake was actually made on 2026-08-07
rather than imagined.

**The path must be outside the repository.** Rule 39 (Prohibited) forbids pushing a secret
"even if it is private and shared only with the lecturer", sanction "severe security failure
and project failure", and rule 40 asks for the gitignore. `.gitignore` is the second line;
this is the first. It matters because the console downloads the client as
`client_secret_<id>.apps.googleusercontent.com.json` — a name that matched none of our
patterns until that day, so a file dropped into the tree was committable.

**The scope must be send-only.** Rule 30 asks for it, and a token found on this machine from
another course assignment carried `gmail.modify` and `calendar` instead: read, alter and
delete on a personal mailbox, plus a calendar nobody needs. It had a live refresh token and
would have worked, which is exactly why nothing would have noticed.

Only the `scopes` member is read. No token, secret or client id is loaded, returned or
logged — checking what a credential is permitted to do does not require handling it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from p2p_thief_agent.shared.private_config import PrivateConfigError

REPORTING_SECTION = "reporting"
SEND_ONLY = "https://www.googleapis.com/auth/gmail.send"
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def credential_path(config: Mapping[str, object]) -> Path:
    """Return the token location from `[reporting].credential_path`, refusing a repo path."""
    section = config.get(REPORTING_SECTION)
    if not isinstance(section, Mapping):
        raise PrivateConfigError(
            f"private config has no [{REPORTING_SECTION}] section; the Gmail token location "
            "belongs there, never in the shared match JSON")
    raw = section.get("credential_path")
    if not isinstance(raw, str) or not raw.strip():
        raise PrivateConfigError(
            f"[{REPORTING_SECTION}].credential_path must name the token file written by the "
            "one-time consent flow (see RUNBOOK_reporting_setup.md)")
    path = Path(raw.strip()).expanduser()
    _refuse_inside_repository(path)
    return path


def _refuse_inside_repository(path: Path) -> None:
    """A credential under the repository root is one `git add -A` from being published."""
    try:
        resolved = path.resolve()
    except OSError as exc:  # pragma: no cover -- an unresolvable path is already a problem
        raise PrivateConfigError(f"cannot resolve credential path {path}: {exc}") from exc
    if resolved == REPOSITORY_ROOT or REPOSITORY_ROOT in resolved.parents:
        raise PrivateConfigError(
            f"the Gmail credential is inside the repository ({resolved}). Rule 39 forbids "
            "pushing a secret even to a private repository, sanction severe security failure "
            "and project failure. Keep it outside the tree and point here [AE-39] [AE-40]")


def assert_send_only(path: Path) -> None:
    """Refuse a token granting more than sending (`AE-30`). Reads only `scopes`.

    Called before the first send rather than at config time, because a token can be
    re-minted between runs and the scope that matters is the one in the file now.
    """
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise PrivateConfigError(f"cannot read the Gmail token at {path}: {exc}") from exc
    try:
        scopes = json.loads(raw).get("scopes")
    except (ValueError, AttributeError) as exc:
        raise PrivateConfigError(f"the Gmail token at {path} is not readable JSON") from exc
    if scopes is None:
        raise PrivateConfigError(
            f"the Gmail token at {path} declares no scopes, so what it permits cannot be "
            "checked. Re-mint it with the consent flow in RUNBOOK_reporting_setup.md")
    if list(scopes) != [SEND_ONLY]:
        raise PrivateConfigError(
            f"the Gmail token at {path} grants {list(scopes)}, not send-only. Rule 30 asks "
            f"for {SEND_ONLY} alone; a broader grant lets a bug in an unattended series "
            "touch mail that has nothing to do with this course [AE-30]")
