# Runbook — Gmail reporting on a fresh machine (`M7-013d`)

Five steps, reproducible by a teammate with no prior context (`G§2.1`).

**Steps 1–3 are yours to run, not an agent's.** They create a real credential on a real
Google account. Nothing in this repository creates, reads or stores one, and no automated
process should be asked to: the consent screen is the point at which a human decides what a
program may do with their mailbox. That is why `M7-013` and `M7-013a` are the only M7 rows
left deliberately unclaimed.

---

## 1. Create the OAuth client

In the Google Cloud console, on a project you own:

1. **APIs & Services → Enable APIs** → enable the **Gmail API**.
2. **OAuth consent screen** → External → add your own address as a **test user**. Test-user
   mode is enough; the app is never published.
3. **Credentials → Create credentials → OAuth client ID → Desktop app**.
4. Download the JSON and save it to the repository root as `credentials.json`.

Ask for exactly one scope:

```
https://www.googleapis.com/auth/gmail.send
```

Rule 30 (Mandatory) requires send-only. `gmail.readonly` or `gmail.modify` would let the
program read the mailbox, and nothing in this project needs to. `GMAIL_SEND_SCOPE` in
`reporting/email_report.py` pins it, and a test asserts no read or modify scope appears.

## 2. Check the credential is ignored before it exists

Run this **before** step 3 writes any token:

```bash
git check-ignore -v credentials.json token.json
```

Both must print a matching `.gitignore` line. Rule 39 (Prohibited) forbids pushing secrets
"even if it is private and shared only with the lecturer", and rule 40 (Mandatory) requires
them gitignored. `.gitignore` covers `credentials.json`, `token.json`, `*credentials*.json`,
`*token*.json`, `*.key`, `*.pem` and `*.p12`.

If either file is already tracked, `git rm --cached` it and rotate the credential in the
Google console. A key that reached a commit is compromised even after the commit is removed —
the object stays in the history of every clone.

## 3. Run the consent flow once

**There is no `p2p-thief authorize` command, and that is deliberate.** `M7-013`/`M7-013a`
are the only M7 rows left unclaimed: the consent screen is where a human decides what a
program may do with their mailbox, so the flow is yours to run. Everything downstream of it
— the refresh policy, the wire format, the send gates — is built and tested against injected
doubles, which is what let the rest of M7 finish without a credential existing.

Add the library and run the flow:

```bash
uv add google-auth-oauthlib
uv run python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
scope = ['https://www.googleapis.com/auth/gmail.send']
creds = InstalledAppFlow.from_client_secrets_file('credentials.json', scope).run_local_server(port=0)
open('token.json','w').write(creds.to_json())
print('token written; refresh token present:', bool(creds.refresh_token))
"
```

A browser window asks you to approve the send-only scope for your own account. Approving
writes `token.json`, containing an access token (about an hour) and a **refresh token**
(months). That refresh token is what makes the rest of the series unattended, and the line
above prints whether you got one without printing the token itself.

Verify without printing anything sensitive:

```bash
uv run python -c "import json,pathlib; d=json.loads(pathlib.Path('token.json').read_text()); print('refresh token present:', bool(d.get('refresh_token')))"
```

It must print `True`. Without a refresh token, `ensure_fresh` refuses once the access token
expires rather than silently skipping a Mandatory report (`AE-32`), and you would discover it
at the end of a series.

## 4. Confirm the gates before the first counted game

```bash
uv run ruff check .
uv run python scripts/check_secrets.py
uv run python scripts/check_file_lengths.py
uv run python -m pytest -q
```

`check_secrets.py` scans every text file in the repository. It has caught two real problems
already — a credential assignment quoted literally in `PROMPT_LOG.md`, and test vectors
shaped like live keys. **Both were fixed at the source; neither was allowlisted.** If it
flags something, change the value: use the placeholder forms it recognises (`dummy-…`,
`placeholder-…`, `${VAR}`, `<replace me>`). An allowlist entry silences the finding *and*
every real value assigned to that line afterwards.

## 5. Rehearse before anything counts

```bash
uv run python -m pytest tests/integration/test_rehearsal.py -q
```

This plays a whole local series with the real builders, audit, settlement, ledgers and
retention store, and a recording transport in place of Gmail. It answers the only question
that matters here: *if we ran a counted game right now, would anything be missing?*

Two companions rehearse the games that go wrong — `test_rehearsal_failures.py` (a technical
loss still produces a complete artifact set) and `test_rehearsal_tampering.py` (a forged
audit is detected, scored, and **not** reported). The last one is worth reading: catching an
opponent's forgery is not a reason to send our own contradicting report, because rule 35
scores a conflict 0 for *both* teams while rule 19 scores a forgery 0 for the falsifying
group alone.

---

## If something fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `no Gmail credential at …` | step 3 not run, or `token.json` deleted | re-run step 3 |
| `there is no refresh token` | consent granted without offline access | delete `token.json`, re-run step 3 |
| `refreshing the access token failed` | the grant was revoked in the Google account | re-run step 3 |
| `refusing to compose a report for a settlement in state …` | the audit did not pass, or the opponent disagreed | do **not** send; preserve the logs and raise it with the lecturer |
| `… was already reported` | a second send for one game | intended — a duplicate risks the rule 35 conflict verdict |
| Secret scan flags a line | a value that looks live | change the value; do not allowlist |

Nothing above ever prints a token. If you need to debug one, note that `TokenState.__repr__`
redacts deliberately — the realistic leak is a token reaching a log through a repr or an
exception message, not through a deliberate print.
