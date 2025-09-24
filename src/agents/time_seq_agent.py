"""Time and sequence normalisation agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.core.base_agent import BaseAgent
from src.pitch.ir import PitchEvent


@dataclass(slots=True)
class TimeSequenceStats:
    gaps: int = 0
    duplicates: int = 0
    regressions: int = 0
    rollovers: int = 0


class TimeSequenceAgent(BaseAgent):
    def __init__(self, policies: Dict[str, int | bool]) -> None:
        super().__init__(name="agent.time_sequence")
        self.policies = policies
        self.stats = TimeSequenceStats()

    def normalize(self, events: List[PitchEvent]) -> List[PitchEvent]:
        if not events:
            return []
        indexed: List[Tuple[int, PitchEvent]] = list(enumerate(events))
        sorted_events = [event for _, event in sorted(indexed, key=lambda item: (item[1].seq, item[1].ts_ns, item[0]))]
        expected_seq = sorted_events[0].seq
        last_ts = sorted_events[0].ts_ns
        normalized: List[PitchEvent] = []
        for event in sorted_events:
            if event.seq != expected_seq:
                if event.seq == 1 and expected_seq == 2 ** 32 - 1 and self.policies.get("allow_rollover", True):
                    self.stats.rollovers += 1
                elif event.seq > expected_seq:
                    self.stats.gaps += 1
                else:
                    self.stats.duplicates += 1
                expected_seq = event.seq
            expected_seq = (event.seq + 1) % (2 ** 32)

            if event.ts_ns < last_ts:
                self.stats.regressions += 1
            last_ts = max(last_ts, event.ts_ns)
            normalized.append(event)
        self.emit(
            "time_seq.normalized",
            gaps=self.stats.gaps,
            duplicates=self.stats.duplicates,
            regressions=self.stats.regressions,
            rollovers=self.stats.rollovers,
        )
        return normalized
