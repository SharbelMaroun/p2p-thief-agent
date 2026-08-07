"""The secret scanner still catches what it is for, after being made more precise.

`scripts/check_secrets.py` gained a type-annotation exclusion, so a dataclass field named
for a credential and annotated with a bare type stops reading as a credential assignment.
That change is only safe if it is narrow, and "narrow" is a claim that needs testing rather
than asserting — a scanner quietly widened is worse than no scanner, because the repository
goes on passing.

So the file below is mostly **positives**: every real shape must still fire. The exclusion
gets three tests; the things it must not swallow get twice that.

This scanner has caught two real problems in this repository already — a credential
assignment quoted literally in `docs/PROMPT_LOG.md`, and test vectors shaped like live keys.
Both were fixed at the source rather than allowlisted, which is the discipline this file
protects.
"""

from __future__ import annotations

import pytest

from scripts.check_secrets import is_dummy, line_findings


def scan(line: str) -> list[str]:
    """Detection only.

    `line_findings` was split out of `findings` for exactly this. The old shape read a file
    and formatted a repository-relative path in one pass, so these rules could only be
    exercised through a file inside the repository — and therefore were not exercised at
    all, which is how a gate the whole secret discipline rests on had no tests of its own.
    """
    return line_findings(line)


def probe(*parts: str) -> str:
    """Join fragments into a credential-shaped string at runtime.

    **The scanner scans this file too**, and it flagged it — correctly — when the probes
    were written as literals. A test file full of live-looking keys fails the very gate it
    exists to protect, and an allowlist entry for it would be the worst possible exemption:
    the one file where a real key would look completely at home.

    So every probe is split across a fragment boundary that breaks the pattern without
    changing the assembled string. The split points are chosen per shape — after the `AKIA`
    prefix, between `BEGIN RSA ` and `PRIVATE KEY`, at the `= ` of an assignment.
    """
    return "".join(parts)


PRIVATE_KEY_HEADER = probe("-----BEGIN RSA ", "PRIVATE KEY-----")
TOKEN_SHAPES = [
    probe("AWS_KEY = AKIA", "IOSFODNN7EXAMPLE"),
    probe("key = ghp_", "0123456789abcdefghijklmnopqrstuvwxyz"),
    probe("openai = sk-", "0123456789abcdefghijklmnopqrst"),
    probe("google = AIza", "SyA0123456789abcdefghijklmnopqrstu"),
    probe("slack = xoxb-", "0123456789-abcdefghij"),
    PRIVATE_KEY_HEADER,
]
ASSIGNMENT_SHAPES = [
    probe('api_key = ', '"live-value-here"'),
    probe('password=', '"hunter2"'),
    probe('client_secret: ', '"GOCSPX-something"'),
    probe('token = ', '"abcdefghijklmnop"'),
]
ANNOTATION_WITH_VALUE = [
    probe("    access_token", ': str = "ya29-a-real-looking-value"'),
    probe("    access_token", ": str = os.environ['TOKEN']"),
]
# Split before the colon for the same reason: a credential name followed by `:` inside a
# string literal is what the assignment pattern is looking for, and it cannot know the
# "value" on the other side is a type.
BARE_ANNOTATIONS = [
    probe("    access_token", ": str"),
    probe("    refresh_token", ": bytes | None"),
    probe("    client_secret", ": Mapping[str, int]"),
    probe("password", ": str"),
]
JSON_MEMBER = probe('  "access_token"', ': "ya29-real-value",')


# --- the exclusion, and its limits ------------------------------------------------------------


@pytest.mark.parametrize("line", BARE_ANNOTATIONS)
def test_a_bare_type_annotation_is_not_a_credential(line: str) -> None:
    """A bare annotation declares that a name exists, never what it holds."""
    assert scan(line) == []


@pytest.mark.parametrize("line", ANNOTATION_WITH_VALUE)
def test_an_annotation_with_a_value_still_fires(line: str) -> None:
    """**The limit that matters.** The exclusion covers the declaration, never the
    assignment — an annotated field with a literal is the same leak as an unannotated one."""
    assert scan(line), f"the scanner missed {line!r}"


def test_the_json_form_still_fires() -> None:
    """A JSON member whose key names a credential and whose value is a string is
    indistinguishable from an annotation to the assignment pattern alone. That is why the
    exclusion requires the **whole line** to be an annotation: quotes around the name
    disqualify it, which is the only difference between the two forms."""
    assert scan(JSON_MEMBER)


# --- everything the scanner is actually for ----------------------------------------------------


@pytest.mark.parametrize("line", TOKEN_SHAPES)
def test_every_known_credential_shape_is_still_caught(line: str) -> None:
    """Parametrised per provider so a regression names which detector broke."""
    assert scan(line), f"the scanner missed {line!r}"


@pytest.mark.parametrize("line", ASSIGNMENT_SHAPES)
def test_assignment_shapes_are_still_caught(line: str) -> None:
    assert scan(line), f"the scanner missed {line!r}"


# --- the placeholder convention -----------------------------------------------------------------


@pytest.mark.parametrize("value", ["dummy-not-a-real-token", "placeholder_x", "your-key-here",
                                   "${GMAIL_TOKEN}", "<replace me>", "changeme"])
def test_the_documented_placeholder_forms_are_recognised(value: str) -> None:
    """Tests and examples need *some* value. These are the forms the scanner accepts, and
    using one is the alternative to an allowlist entry."""
    assert is_dummy(value)


@pytest.mark.parametrize("value", ["ya29.realish", "sk-abcdef", "hunter2"])
def test_a_value_that_merely_looks_harmless_is_not_a_placeholder(value: str) -> None:
    assert not is_dummy(value)
