"""`M6-016`: internal belief stays private; only the agreed observation crosses the wire.

The Thief's belief over the Cop's position — and the trust it assigns a hint — is local
certainty. It must never travel: what crosses is the public `TurnMessage`, whose only scent
member is the sparse `smell_grid` observation. Two guards enforce this. The turn roster is
pinned, so no belief or certainty field can be added to the wire unnoticed; and the wire and
transport layers are proven never to import the inference modules, so belief cannot reach a
message even indirectly.
"""

from dataclasses import fields
from pathlib import Path

from p2p_thief_agent.protocol.wire import TurnMessage

_SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent"
WIRE_LAYERS = (_SRC / "protocol", _SRC / "adapters")

# The private inference/certainty modules. Nothing that serialises to the wire may import
# them, or belief could leak beyond the agreed fields.
PRIVATE_INFERENCE = (
    "perception.belief", "perception.consume", "perception.trust",
    "perception.hint", "strategy.belief_policy",
    "apply_evidence", "uniform_belief", "scent_likelihood", "trust_weighted",
)


def test_the_turn_message_roster_carries_no_belief_or_certainty_field() -> None:
    roster = {f.name for f in fields(TurnMessage)}
    assert roster == {
        "step", "sender", "hint", "smell_grid", "commit", "timestamp",
        "barrier_placed", "capture_claim", "claim_response", "win_claim",
    }
    assert not any(any(marker in name for marker in ("belief", "certainty", "prob", "trust"))
                   for name in roster)


def test_the_wire_and_transport_layers_never_import_the_inference_modules() -> None:
    offenders: list[tuple[str, str]] = []
    for layer in WIRE_LAYERS:
        for path in layer.rglob("*.py"):
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped.startswith(("import ", "from ")):
                    continue
                offenders += [(path.name, stripped) for token in PRIVATE_INFERENCE
                              if token in stripped]
    assert offenders == [], f"the wire layer must not import private inference: {offenders}"
