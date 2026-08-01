"""`M5-001b`: no subsystem imports another; they meet only at the gateway.

Book chapter 9 puts all communication between the five subsystems through the
Orchestrator. This guard walks `src/` and fails on any direct import from one subsystem
to another. Shared layers (domain, protocol, shared, `services.limits`, the gatekeeper)
and the orchestration/gateway layer itself are not subsystems, so importing them is
allowed — the gateway *must* import all five, which is the whole point.
"""

from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_thief_agent"

# The book's five orchestrator subsystems, as dotted-module prefixes under the package.
SUBSYSTEMS = {
    "mcp_connector": ("adapters", "peer"),
    "decision_module": ("strategy", "state.policy"),
    "log_manager": ("services.log_manager",),
    "deadline_tracker": ("services.deadlines",),
    "watchdog": ("services.watchdog",),
}


def subsystem_of(module: str) -> str | None:
    for name, prefixes in SUBSYSTEMS.items():
        if any(module == p or module.startswith(p + ".") for p in prefixes):
            return name
    return None


def module_path(path: Path) -> str:
    parts = [p for p in path.relative_to(SRC).with_suffix("").parts if p != "__init__"]
    return ".".join(parts)


def imported_modules(path: Path):
    prefix = "p2p_thief_agent."
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("from " + prefix):
            yield stripped[len("from " + prefix):].split(" import")[0].strip()
        elif stripped.startswith("import " + prefix):
            yield stripped[len("import " + prefix):].split()[0].strip()


def test_no_subsystem_imports_another_directly() -> None:
    offenders: list[tuple[str, str, str, str]] = []
    for path in SRC.rglob("*.py"):
        mine = subsystem_of(module_path(path))
        if mine is None:
            continue
        for imported in imported_modules(path):
            theirs = subsystem_of(imported)
            if theirs is not None and theirs != mine:
                offenders.append((module_path(path), imported, mine, theirs))
    assert offenders == [], f"subsystems must meet only at the gateway: {offenders}"
