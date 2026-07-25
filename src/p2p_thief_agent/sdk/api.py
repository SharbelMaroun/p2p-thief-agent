"""Public SDK entry point for all future Thief business behavior."""

from dataclasses import dataclass, field

from p2p_thief_agent.shared import __version__


@dataclass(frozen=True, slots=True)
class ThiefSdk:
    """Identify the behavior-free Thief SDK scaffold."""

    role: str = field(default="thief", init=False)
    version: str = field(default=__version__, init=False)
