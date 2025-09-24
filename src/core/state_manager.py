"""Shared state container for agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class StateManager:
    """Minimal key-value state store."""

    _state: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._state.get(key, default)

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._state)
