"""Weight a hint by the sender's running trust, and update that trust (`M6-003b`/`M6-003f`).

A hint is evidence only to the degree the opponent has earned belief. `trust_weighted`
tempers a decoded hint's likelihood toward uniform by `(1 - trust)`, so a low-trust hint
barely moves the belief and a zero-trust one is ignored entirely. `update_trust` then
moves that trust by comparing the hint against the Cop's own **scent**: a hint that
concentrates where scent does is corroborated and earns trust; one that points where scent
shows nothing is a claimed direction with no residue behind it — evidence of a lie — and
loses it. Trust stays clipped to `[0, 1]`.
"""

from __future__ import annotations

from collections.abc import Sequence

from p2p_thief_agent.perception.belief import BeliefError, Grid, normalize, uniform_belief

NEUTRAL_TRUST = 0.5
DEFAULT_TRUST_RATE = 0.2


def _check_unit(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise BeliefError(f"{name} must be in [0, 1], got {value}")


def trust_weighted(likelihood: Sequence[Sequence[float]], trust: float) -> Grid:
    """Temper a hint's likelihood toward uniform by `(1 - trust)` (`M6-003b`).

    At `trust = 1` the hint applies in full; at `trust = 0` it collapses to uniform and so
    changes nothing when fed through `apply_evidence`.
    """
    _check_unit("trust", trust)
    scaled = normalize(likelihood)
    flat = uniform_belief(len(scaled), len(scaled[0]))
    return tuple(
        tuple(trust * odds + (1.0 - trust) * even for odds, even in zip(srow, frow, strict=True))
        for srow, frow in zip(scaled, flat, strict=True)
    )


def update_trust(
    trust: float,
    hint_likelihood: Sequence[Sequence[float]],
    scent_belief: Sequence[Sequence[float]],
    *,
    rate: float = DEFAULT_TRUST_RATE,
) -> float:
    """Raise trust when the hint agrees with scent, lower it when it contradicts (`M6-003f`).

    Agreement is the overlap `Σ hint·scent`. Measured against the overlap a wholly
    uninformative (uniform) hint would score, an above-baseline hint is corroborated and an
    at-or-below-baseline one is not. The signal is clipped to `[-1, 1]`, so one hint can
    move trust by at most `rate`.
    """
    _check_unit("trust", trust)
    _check_unit("rate", rate)
    hint = normalize(hint_likelihood)
    scent = normalize(scent_belief)
    if [len(row) for row in hint] != [len(row) for row in scent]:
        raise BeliefError("hint and scent must share the same shape")
    agreement = sum(h * s for hrow, srow in zip(hint, scent, strict=True)
                    for h, s in zip(hrow, srow, strict=True))
    baseline = 1.0 / (len(hint) * len(hint[0]))
    signal = max(-1.0, min(1.0, agreement / baseline - 1.0))
    return min(1.0, max(0.0, trust + rate * signal))
