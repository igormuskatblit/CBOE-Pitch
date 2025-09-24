"""Base class for infrastructure agents."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class BaseAgent:
    """Shared behaviour for all agents."""

    name: str
    logger: logging.Logger = field(init=False)

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(self.name)
        self.logger.debug("agent.init", extra={"agent": self.name})

    def emit(self, event: str, **kwargs: Any) -> None:
        payload: Dict[str, Any] = {"agent": self.name}
        payload.update(kwargs)
        self.logger.info(event, extra=payload)
