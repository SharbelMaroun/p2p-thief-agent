"""`M7-014a` / `M7-014c`: the report as an attachment, encoded as the API expects.

Two encoding mistakes here are silent, and both are tested against directly:

* **standard base64 instead of base64url** — the alphabets differ in two characters, `+/`
  versus `-_`, so a message encodes identically under either unless its bytes happen to hit
  those two values. That is the worst possible failure shape: it passes every casually
  written test and breaks on some real report. `alphabet_probe` below is constructed to hit
  them deterministically, because the obvious fixture — a composed report — cannot: its
  payload is *already* base64 by the time the outer encoder sees it.
* **stripped padding** — the widely-copied idiom comes from JWT, where padding is
  *forbidden*. Gmail's `raw` field is a different specification, and `urlsafe_b64encode`
  emits padding, so it is kept.

The call shape lives in `test_gmail_send_call.py`. Nothing in either file touches a
credential or opens a connection, which is what makes the wire format provable while
`M7-013`/`M7-013a` stay unclaimed pending the operator's own consent flow.
"""

from __future__ import annotations

import base64
import json
from email.message import EmailMessage

from p2p_thief_agent.reporting.email_report import compose_report
from p2p_thief_agent.reporting.gmail_wire import (
    decode_raw,
    encode_raw,
    send_body,
)

AGREED = {"state": "agreed", "our_outcome": "survival", "their_outcome": "survival",
          "audit_passed": True, "audit_failed_at": None}
RESULT = {"total_score": 25, "sub_games": [{"n": n, "tokens": 1000 + n} for n in range(1, 7)]}


def message():
    """A fresh report each call.

    **Each one differs**: `EmailMessage` picks a random MIME boundary, so two messages built
    from identical inputs are not byte-identical. Any test comparing an encoding against a
    re-built message compares two different documents — which is how the first draft of the
    round-trip test below failed.
    """
    return compose_report(result=RESULT, settlement=AGREED, sender="me@example.com",
                          game_id="g42", team_code="sharNamr")


def alphabet_probe() -> EmailMessage:
    """A message whose bytes are guaranteed to encode differently under the two alphabets.

    Not `compose_report` output, deliberately. A real report's payload is *already*
    base64-encoded by `add_attachment`, so the outer encoding sees ASCII and may contain no
    `+` or `/` at all — the first draft of this file asserted a difference its own fixture
    could not produce.

    `?` (0x3F) and `~` (0x7E) both end in the six bits `111111` and `111110`, so whenever
    one lands at an offset ≡ 2 (mod 3) it becomes `/` or `+` under the standard alphabet.
    Repeating the pair covers every residue class many times over, which makes this
    deterministic rather than probable.
    """
    probe = EmailMessage()
    probe["To"] = "someone@example.com"
    probe["Subject"] = "alphabet probe"
    probe.set_content("~?" * 64)
    return probe


# --- the encoding ------------------------------------------------------------------------------


def test_the_encoding_is_base64url_and_not_standard_base64() -> None:
    """**The mistake that only shows up on some messages.** The two alphabets agree except
    on `+/` versus `-_`, so a message encodes identically under both unless its bytes
    happen to hit those two values — which is why the probe is constructed to hit them."""
    probe = alphabet_probe()
    standard = base64.b64encode(probe.as_bytes()).decode("ascii")
    assert "+" in standard and "/" in standard, "the probe cannot tell the alphabets apart"
    raw = encode_raw(probe)
    assert "+" not in raw and "/" not in raw
    assert raw != standard


def test_the_encoding_is_reversible_by_a_base64url_decoder() -> None:
    """The other half: absent `+/` would also be satisfied by an encoder that dropped them.
    This pins the output to something a standards-compliant reader recovers exactly."""
    probe = alphabet_probe()
    assert base64.urlsafe_b64decode(encode_raw(probe)) == probe.as_bytes()


def test_padding_is_kept() -> None:
    """The stripping idiom comes from JWT, where padding is forbidden. Gmail's `raw` is a
    different field in a different specification."""
    probe = alphabet_probe()
    raw = encode_raw(probe)
    assert len(raw) % 4 == 0
    if len(probe.as_bytes()) % 3:
        assert raw.endswith("=")


def test_the_message_round_trips_through_the_wire_body() -> None:
    """Round-tripped rather than compared against a constant — an encoder checked against a
    string somebody derived with the same mistaken idiom proves only that the mistake is
    consistent. **One message, encoded and decoded**: re-building it would produce a
    different MIME boundary and a spurious failure."""
    report = message()
    assert decode_raw(send_body(report)) == report.as_bytes()


def test_the_attachment_survives_the_encoding_intact() -> None:
    """`M7-014a`. The point of the envelope is the payload inside it, so the assertion goes
    all the way back to the parsed JSON rather than stopping at "the bytes match"."""
    import email  # noqa: PLC0415

    recovered = email.message_from_bytes(decode_raw(send_body(message())),
                                         policy=email.policy.default)
    attachments = list(recovered.iter_attachments())
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "result_g42.json"
    assert json.loads(attachments[0].get_payload(decode=True))["total_score"] == 25


def test_the_body_carries_no_part_of_the_report() -> None:
    """`AE-34`: the report is an attachment, never body text. Checked after the round trip,
    because that is the form the recipient actually receives."""
    import email  # noqa: PLC0415

    recovered = email.message_from_bytes(decode_raw(send_body(message())),
                                         policy=email.policy.default)
    body = recovered.get_body(preferencelist=("plain",)).get_content()
    assert "total_score" not in body and "25" not in body
