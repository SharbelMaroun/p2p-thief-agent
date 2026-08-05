"""`M7-004`: verbal-provider modes route through the gate and fall back deterministically."""

from p2p_thief_agent.services.gatekeeper import Gatekeeper
from p2p_thief_agent.verbal.generation import generate_hint
from p2p_thief_agent.verbal.providers import gated_model_provider


def test_a_model_call_routes_through_the_gatekeeper() -> None:
    """`M7-003a`: a model provider's call is admitted by the one gatekeeper."""
    gate = Gatekeeper(requests_per_minute=30, concurrent_requests=2, queue_depth=10)
    provider = gated_model_provider(gate, lambda step: f"model says {step}", lambda: 0.0)
    assert provider(3) == "model says 3"
    assert gate.queue_status().admitted == 1  # it went through the gate


def test_a_blocked_provider_falls_back_to_the_template() -> None:
    """`M7-004a`: with the gate full, the provider raises and the hint falls back — no stall."""
    gate = Gatekeeper(requests_per_minute=30, concurrent_requests=1, queue_depth=10)
    gate.submit("holding the only slot", now=0.0)  # gate is now at capacity
    provider = gated_model_provider(gate, lambda step: "hint from the ether", lambda: 0.0)
    hint = generate_hint(0, provider=provider, every_n_steps=1)
    assert hint.text == generate_hint(0).text  # the token-free template


def test_a_failing_model_falls_back_to_the_template() -> None:
    def broken(_step: int) -> str:
        raise RuntimeError("model unreachable")

    gate = Gatekeeper(requests_per_minute=30, concurrent_requests=2, queue_depth=10)
    provider = gated_model_provider(gate, broken, lambda: 0.0)
    assert generate_hint(0, provider=provider, every_n_steps=1).text == generate_hint(0).text
