"""`M6-024`: hint generation never blocks the turn deadline.

Generation is bounded or skipped, never awaited indefinitely. The default path makes no
external call, so a whole series of hints costs negligible time; and a model provider — the
only thing that could be slow — is reached at most once every N steps, and a provider that
fails or is absent falls back to the token-free template (`M6-013b`). A model provider is
expected to carry its own LLM deadline through the gatekeeper (`M7-003`); generation itself
never awaits it every turn.
"""

import time

from p2p_thief_agent.verbal.generation import generate_hint


def test_token_free_generation_of_a_full_series_is_negligible() -> None:
    """The default path makes no external call, so it cannot block the deadline."""
    start = time.perf_counter()
    for step in range(6 * 35):
        generate_hint(step)
    assert (time.perf_counter() - start) * 1000 < 100  # < 100 ms for 210 hints


def test_a_model_provider_is_reached_at_most_once_every_n_steps() -> None:
    """`M6-024`/`M6-008f`: gating bounds how often a possibly-slow model is awaited."""
    calls: list[int] = []

    def provider(step: int) -> str:
        calls.append(step)
        return "the streets are quiet tonight"

    for step in range(30):
        generate_hint(step, provider=provider, every_n_steps=5)
    assert calls == [0, 5, 10, 15, 20, 25]  # never every turn
