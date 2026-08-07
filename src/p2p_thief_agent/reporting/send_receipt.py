"""What our side can actually prove about sending a report (`M9-010c`).

The book names three layers of proof, and they are not interchangeable:

1. **Receipt at the lecturer's address** (p.78/183). "Sending the two separate reports is
   the condition for both groups to receive their points", and if a report is not received
   from one side, "that side will not be credited for the game". This is the layer that
   decides the points — and it is the one **we cannot observe**. Only the recipient can.
2. **Cryptographic mutual agreement** — the `mutual_agreement` block in the result, carrying
   a SHA-256 and `confirmed: true`.
3. **A `Verified OK` screenshot** from the Replay app (p.81/189, "absolute mandatory").

This module holds layer 1 as far as a *sender* can honestly take it: the provider accepted
the message and returned an id, at a recorded time, to a recorded address. The class is named
`SendReceipt` and not `ProofOfDelivery` for that reason, and `as_record` writes the
distinction into the artifact rather than leaving a reader to infer it.

**The reference implementation records nothing at all.** Its sender returns `{status,
reason}` for a CLI line and none of it reaches the four artifacts, so after a series the only
evidence a report was sent is somebody's memory.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


class EvidenceError(ValueError):
    """Raised when evidence would claim more than it can support."""


@dataclass(frozen=True, slots=True)
class SendReceipt:
    """What our side observed when it sent one report. **Not proof of receipt.**"""

    game_id: str
    message_id: str
    sent_at: str
    recipient: str

    def __post_init__(self) -> None:
        for name in ("game_id", "message_id", "sent_at", "recipient"):
            if not getattr(self, name):
                raise EvidenceError(f"a send receipt needs a non-empty {name}")

    @classmethod
    def from_api_response(cls, response: Mapping[str, object], *, game_id: str,
                          sent_at: str, recipient: str) -> SendReceipt:
        """Read the id out of a `users().messages().send` response.

        A response with no id is refused rather than stored as an empty string. Afterwards,
        a report that failed to send and one that sent without a receipt look identical —
        and only one of them costs the game's points.
        """
        message_id = response.get("id")
        if not isinstance(message_id, str) or not message_id:
            raise EvidenceError(
                f"the send response for {game_id!r} carries no message id, so nothing "
                "evidences the send; rule 32 makes reporting Mandatory and a report whose "
                "delivery cannot be shown is indistinguishable from one never sent [AE-32]")
        return cls(game_id=game_id, message_id=message_id, sent_at=sent_at,
                   recipient=recipient)

    def as_record(self) -> dict[str, str]:
        """The receipt as it enters the bundle, with its own limits stated."""
        return {"game_id": self.game_id, "message_id": self.message_id,
                "sent_at": self.sent_at, "recipient": self.recipient,
                "evidences": "API acceptance, not receipt by the lecturer"}
