"""Summary statistics for the parameter research (`M9-006c`).

`M9-006c` asks for "experiment tables with **run counts**, not anecdotes"; the book sets the
standard plainly — research "based on numbers and not on guesses" (p.142/266). So no figure
here appears without the number of runs behind it, and no mean appears without its spread.

**The design here is deterministic, and that changes what the numbers mean.** The companion
repository pairs on random seeds; this repository's harness is a fixed pursuing Cop on fixed
start scenarios, so there is no sampling noise at all — a difference between two arms on one
scenario is exact, not an estimate. The cost is coverage: four scenarios is four data
points, so the experiments widen the scenario set systematically rather than repeating a
run that would return the identical answer. Repeating a deterministic run inflates `n`
without adding a single bit of evidence, which is the one way a run count can lie.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Summary:
    """A measured quantity, never separated from how many runs produced it."""

    runs: int
    mean: float
    stdev: float
    minimum: float
    q1: float
    median: float
    q3: float
    maximum: float

    @property
    def five_number(self) -> tuple[float, float, float, float, float]:
        """What a box plot draws: min, Q1, median, Q3, max."""
        return (self.minimum, self.q1, self.median, self.q3, self.maximum)

    def as_dict(self) -> dict[str, float | int]:
        return {"runs": self.runs, "mean": round(self.mean, 4),
                "stdev": round(self.stdev, 4), "min": round(self.minimum, 4),
                "q1": round(self.q1, 4), "median": round(self.median, 4),
                "q3": round(self.q3, 4), "max": round(self.maximum, 4)}


def quantile(values: Sequence[float], fraction: float) -> float:
    """Linear-interpolated quantile; refuses an empty sample.

    Interpolation matters at these sizes: with a few dozen scenarios a nearest-rank Q1
    moves in visible steps, so two genuinely different configurations would draw identical
    boxes.
    """
    if not values:
        raise ValueError("cannot take a quantile of no values")
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    weight = position - lower
    upper = min(lower + 1, len(ordered) - 1)
    return float(ordered[lower] * (1 - weight) + ordered[upper] * weight)


def summarise(values: Sequence[float]) -> Summary:
    """Reduce measurements to a reportable summary. Refuses an empty sample."""
    if not values:
        raise ValueError("a summary of zero runs would be an anecdote, not a measurement")
    runs = len(values)
    mean = sum(values) / runs
    # Sample standard deviation. Even with a deterministic harness these are scenarios
    # drawn from a much larger space of possible openings, not the whole population.
    variance = sum((v - mean) ** 2 for v in values) / (runs - 1) if runs > 1 else 0.0
    return Summary(runs=runs, mean=mean, stdev=sqrt(variance), minimum=float(min(values)),
                   q1=quantile(values, 0.25), median=quantile(values, 0.5),
                   q3=quantile(values, 0.75), maximum=float(max(values)))


@dataclass(frozen=True)
class PairedResult:
    """A per-scenario comparison of two arms facing the identical pursuing Cop."""

    pairs: int
    wins: int
    losses: int
    ties: int

    @property
    def decisive(self) -> int:
        return self.wins + self.losses

    @property
    def win_share(self) -> float:
        """Share of the *decisive* pairs won; ties carry no information either way."""
        return self.wins / self.decisive if self.decisive else 0.0

    def as_dict(self) -> dict[str, float | int]:
        return {"pairs": self.pairs, "wins": self.wins, "losses": self.losses,
                "ties": self.ties, "win_share_of_decisive": round(self.win_share, 4)}


def paired_compare(candidate: Sequence[float], baseline: Sequence[float]) -> PairedResult:
    """Compare two arms scenario by scenario. Refuses unequal arms rather than truncating.

    Equal lengths are load-bearing: the arms are comparable only because scenario *i* gave
    both the identical Cop and opening, so zipping a short arm against a long one would
    pair unrelated matches and produce a number that reads exactly like evidence.
    """
    if len(candidate) != len(baseline):
        raise ValueError(
            f"{len(candidate)} candidate runs against {len(baseline)} baseline runs; "
            "a paired comparison needs the same scenarios on both sides")
    wins = sum(1 for a, b in zip(candidate, baseline, strict=True) if a > b)
    losses = sum(1 for a, b in zip(candidate, baseline, strict=True) if a < b)
    return PairedResult(pairs=len(candidate), wins=wins, losses=losses,
                        ties=len(candidate) - wins - losses)
