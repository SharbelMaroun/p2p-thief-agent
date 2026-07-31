"""Whether this peer will agree to play at all (`M5-014`).

`handshake.py` owns the *mechanics* of the signed-terms exchange -- assembling the
message, signing it, checking a signature. This module owns the *policy*: the
Appendix F floors, who the participants must be, and what a refusal has to say.

Appendix E rule 11 makes refusal mandatory on any mismatch and rule 12 forbids
weakening a `Minimum`, so both are decided here, before a first move exists. A
refusal names the offending term: the reference implementation's own failure path
reports which terms are at fault rather than a bare "no", and a refusal an opponent
cannot act on is worth little to either side.

Appendix F statuses come from this repository's `docs/PARAMETERS_BASELINE.md`,
which reads them from the book's tables 13, 15, 16, and 18 (`THIEF-002`: no peer
repository is an input).
"""

from __future__ import annotations

from collections.abc import Mapping

from p2p_thief_agent.protocol.crypto import CryptoError, commit_of
from p2p_thief_agent.protocol.handshake import missing_required_terms

# `FIXED` (table 16 scent, table 18 series): any deviation at all is a refusal.
FIXED_TERMS: dict[str, object] = {
    "smell_grid_size": 5,
    "decay_per_step": 0.10,
    "emit_intensity": 0.9,
    "num_games": 6,
}
# `MINIMUM` (tables 13, 15): may move only in the harder direction, never below.
MINIMUM_TERMS: dict[str, int] = {"board_size": 7, "max_steps": 35, "barriers_max": 14}

OFFER_FIELDS = ("terms", "nonce", "signature")


class AgreementError(ValueError):
    """Raised when an offer is malformed, unsigned, or not acceptable to play."""


def check_appendix_f(terms: Mapping) -> None:
    """Refuse an altered `FIXED` value or a weakened `MINIMUM` one `[AE-12]`."""
    for name, required in FIXED_TERMS.items():
        if terms.get(name) != required:
            raise AgreementError(f"{name} is FIXED at {required}; offer carries {terms.get(name)!r}")
    for name, floor in MINIMUM_TERMS.items():
        value = terms.get(name)
        if isinstance(value, bool) or not isinstance(value, int):
            raise AgreementError(f"{name} must be a whole number, got {value!r}")
        if value < floor:
            raise AgreementError(f"{name} is a MINIMUM of {floor}; offer weakens it to {value}")


def differing_terms(mine: Mapping, theirs: Mapping) -> list[str]:
    """Return every term the two sides disagree on, by name and sorted.

    Compared over the union of both key sets, so a term the opponent simply left
    out is a disagreement rather than an invisible default.
    """
    return sorted(
        name for name in set(mine) | set(theirs) if mine.get(name) != theirs.get(name)
    )


def validate_participants(participants: object, group_id: object = None) -> None:
    """Require exactly two distinct named groups, including this one if given."""
    if not isinstance(participants, list) or len(participants) != 2:
        raise AgreementError("the agreement must name exactly two participants")
    if not all(isinstance(name, str) and name.strip() for name in participants):
        raise AgreementError("participant names must be non-empty strings")
    if participants[0] == participants[1]:
        raise AgreementError("the two participants must be distinct")
    if group_id is not None and group_id not in participants:
        raise AgreementError(f"group {group_id!r} is not one of the participants")


def accept_offer(message: Mapping, my_terms: Mapping) -> dict:
    """Return the agreed terms, or raise naming exactly what stops the match.

    The order is deliberate. Structure first, because nothing else can be trusted
    without it; then the signature, so the terms being judged are the ones the
    opponent actually committed to; then Appendix F, which is absolute; and only
    then equality with our own terms, which is the one an opponent can fix.
    """
    for field in OFFER_FIELDS:
        if field not in message:
            raise AgreementError(f"offer is missing {field!r}")
    terms = message["terms"]
    if not isinstance(terms, Mapping):
        raise AgreementError("offer terms must be an object")
    if commit_of(dict(terms), message["nonce"]) != message["signature"]:
        raise AgreementError("offer signature does not cover the offered terms")
    incomplete = missing_required_terms(terms)
    if incomplete:
        raise AgreementError(f"offer is missing required agreed term(s): {', '.join(incomplete)}")
    check_appendix_f(terms)
    differing = differing_terms(my_terms, terms)
    if differing:
        raise AgreementError(f"agreed terms differ on: {', '.join(differing)}")
    return dict(terms)


def signed_offer_is_valid(message: Mapping) -> bool:
    """Return whether an offer's signature covers its own terms (no policy)."""
    try:
        return commit_of(dict(message["terms"]), message["nonce"]) == message["signature"]
    except (CryptoError, KeyError, TypeError):
        return False
