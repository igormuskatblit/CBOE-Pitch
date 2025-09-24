"""Simple agent bus for orchestrating ordered execution."""
from __future__ import annotations

from typing import Callable, List


class AgentBus:
    """Executes callables in a fixed order."""

    __slots__ = ("_steps",)

    def __init__(self) -> None:
        self._steps: List[Callable[[], None]] = []

    def add_step(self, func: Callable[[], None]) -> None:
        self._steps.append(func)

    def run(self) -> None:
        for step in self._steps:
            step()
