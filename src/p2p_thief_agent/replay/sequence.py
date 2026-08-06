"""Structural integrity of a log's step sequence (`M8-008d`) — reported, never bannered.

Every commitment covers one record. Shuffling the records, deleting one, or duplicating one
therefore leaves **every digest valid**, and a verifier built only on hashes stamps
`Verified OK` on all three. `M8-008d` asks us to detect that.

**Why this is a separate report and not part of the verdict.** Asked directly, both sources
say sequence checking is neither required nor implemented:

* The **book**: rule 19 is "any mismatch **in the digest**" (p.129/271) — structural damage
  is not rule 19. There is no standalone rule requiring contiguous numbering. A missing step
  instead produces "contradictory reports" between the peers → **rule 35** (p.131/275),
  whose sanction falls on *both* teams, and shows an illegal state jump → **rule 5**.
* The **reference**: `verify_record` checks each record "completely independently … with no
  reference to its place in the sequence or the value of the `step` field"; `normalize_log`
  neither sorts nor re-indexes; nothing anywhere rejects a duplicate or missing step. Its
  own summary: step sequence is *passive*, each step "a cryptographic island standing alone".

So a log ordered differently from ours is **not evidence of forgery**, and red-bannering one
would be a false accusation carrying "no appeal process" (`:1769`) — with rule 35 scoring
zero for *both* teams if we then file a contradicting report. Being stricter than the
specification is the dangerous direction here, not the safe one.

The honest resolution is to detect and *report* it while leaving the cryptographic banner to
the cryptography. What an anomaly means is then a settlement question — decided by comparing
**both** logs under rule 35 — not something a single-log viewer may decide alone.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class SequenceFinding:
    """One structural anomaly, named so an operator can act on the right rule."""

    kind: str
    detail: str
    rule: str


@dataclass(frozen=True)
class SequenceReport:
    """What the numbering says, kept apart from what the digests say."""

    steps: tuple[object, ...]
    findings: tuple[SequenceFinding, ...]

    @property
    def contiguous(self) -> bool:
        return not self.findings

    @property
    def summary(self) -> str:
        if self.contiguous:
            return f"sequence intact — {len(self.steps)} steps, 1..{len(self.steps)}"
        return "; ".join(f"{f.kind}: {f.detail} [{f.rule}]" for f in self.findings)


def inspect_sequence(records: Sequence[Mapping[str, object]]) -> SequenceReport:
    """Report gaps, duplicates and out-of-order steps. Never raises, never verdicts."""
    steps = tuple(
        record.get("step") if isinstance(record, Mapping) else None for record in records
    )
    findings: list[SequenceFinding] = []

    numbered = [s for s in steps if isinstance(s, int) and not isinstance(s, bool)]
    if len(numbered) != len(steps):
        findings.append(SequenceFinding(
            "unnumbered", f"{len(steps) - len(numbered)} record(s) carry no integer step",
            "AE-5",
        ))
    if not numbered:
        return SequenceReport(steps, tuple(findings))

    duplicates = sorted({s for s in numbered if numbered.count(s) > 1})
    if duplicates:
        findings.append(SequenceFinding(
            "duplicate", f"step(s) {duplicates} appear more than once",
            "AE-35",  # two records claiming one step is a self-contradicting report
        ))
    if numbered != sorted(numbered):
        findings.append(SequenceFinding(
            "out-of-order", f"steps are not ascending: {numbered}",
            "AE-5",  # replaying them in file order shows an illegal state transition
        ))
    expected = set(range(min(numbered), max(numbered) + 1))
    gaps = sorted(expected - set(numbered))
    if gaps:
        findings.append(SequenceFinding(
            "gap", f"step(s) {gaps} are missing from the log",
            "AE-35",  # a log that is not "full" produces contradictory reports (p.39/102)
        ))
    return SequenceReport(steps, tuple(findings))
