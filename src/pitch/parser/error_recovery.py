"""Recovery context tracking parse anomalies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class RecoveryContext:
    warnings: List[str] = field(default_factory=list)

    def record_failure(self, offset: int, reason: str) -> None:
        self.warnings.append(f"recovered@{offset}:{reason}")

    def reset(self) -> None:
        self.warnings.clear()
