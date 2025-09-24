"""Intermediate representation for parsed PITCH events."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(slots=True)
class PitchEvent:
    seq: int
    unit: int
    ts_ns: int
    msg_type: str
    raw: bytes
    f: Dict[str, int]
    meta: Dict[str, object]

    def to_json(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["raw"] = self.raw.hex()
        return payload


@dataclass(slots=True)
class PitchEventBatch:
    events: List[PitchEvent]

    def to_json(self) -> List[Dict[str, object]]:
        return [event.to_json() for event in self.events]
