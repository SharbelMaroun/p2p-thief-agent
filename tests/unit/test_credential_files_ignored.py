"""Rule 39/40: the credential filenames a user actually receives are ignored.

Rule 40 says to gitignore credential files; rule 39 forbids pushing a secret "even if it is
private and shared only with the lecturer", with the sanction "severe security failure and
project failure". The `.gitignore` covered `token.json` and `credentials.json` from the
start — and missed the one file anybody actually ends up holding.

The Google Cloud console does not offer you `credentials.json`. It downloads
`client_secret_<numbers>-<hash>.apps.googleusercontent.com.json`, which matches neither
`*credentials*.json` nor `*token*.json`. So the single file a real user drags into the
repository was the single file that would have been committed. Found 2026-08-07.

`git check-ignore` is asked rather than the pattern list being read, because what protects
the repository is Git's answer, not a string appearing in a file.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Realistic names, not invented ones: the console default, the classic, the service-account
# variants, and private keys.
CREDENTIAL_NAMES = [
    "client_secret_1234567890-abcdefg.apps.googleusercontent.com.json",
    "client_secret.json",
    "credentials.json",
    "token.json",
    "service_account.json",
    "my-service-account-key.json",
    "server.pem",
    ".env",
]


def ignored(name: str) -> bool:
    """Ask Git, not the pattern file. Exit 0 means the path is ignored."""
    done = subprocess.run(["git", "check-ignore", "-q", name], cwd=ROOT, capture_output=True)
    return done.returncode == 0


@pytest.mark.parametrize("name", CREDENTIAL_NAMES)
def test_a_credential_file_would_not_be_committed(name: str) -> None:
    assert ignored(name), (
        f"{name} is not ignored. Rule 39's sanction is severe security failure and project "
        "failure, and this is the shape the mistake takes: a real download, dropped in, "
        "committed without anyone deciding to")


def test_an_ordinary_source_file_is_still_tracked() -> None:
    """The guard on the guard. A `.gitignore` of `*` would pass every test above."""
    assert not ignored("README.md")
    assert not ignored("src/x.py")
