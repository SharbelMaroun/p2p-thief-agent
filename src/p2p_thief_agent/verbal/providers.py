"""Private verbal-provider modes, with deterministic fallback (`M7-004`).

The verbal game's default is the zero-token template (`M6-008`). An operator may instead
configure a model provider — a local Ollama, an API, or a CLI (`PROJECT_CONTEXT §11`) — in the
private TOML. Whatever the mode, a model call must route through the **one** gatekeeper
(`M7-003a`) and must never stall a turn.

`gated_model_provider` wraps a model behind the gate. If the gate is at capacity, or the model
itself fails, the returned provider raises — and `generate_hint` catches any provider error and
falls back to the token-free template (`M7-004a`, `M6-013b`). So a blocked or broken provider
costs a plain template hint, not a forfeited turn; and the move is untouched either way, since
the language model never selects it (`AE-25`).
"""

from __future__ import annotations

from collections.abc import Callable

from p2p_thief_agent.services.gatekeeper import Gatekeeper, guard

# Accepted modes; the model sub-type (ollama / api / cli) is the operator's plugin choice.
TEMPLATE_MODE = "template"
MODEL_MODE = "model"

ModelCall = Callable[[int], str]  # given a step, return a candidate hint (may fail)
Clock = Callable[[], float]


def gated_model_provider(gatekeeper: Gatekeeper, model: ModelCall, clock: Clock) -> ModelCall:
    """Return a provider that routes a model call through the gatekeeper (`M7-003a`).

    Hand the result to `generate_hint`. If the gate has no capacity the guard raises, and if
    the model fails it raises; either way `generate_hint` falls back to the template, so the
    turn is never stalled (`M7-004a`).
    """

    def provider(step: int) -> str:
        return str(guard(gatekeeper, lambda: model(step), clock()))

    return provider
