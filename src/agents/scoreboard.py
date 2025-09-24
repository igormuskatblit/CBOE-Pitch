"""Scoreboard agent aligning events with golden model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from src.core.base_agent import BaseAgent
from src.pitch.golden_book import GoldenBookState
from src.pitch.ir import PitchEvent
from src.utils.hash_utils import compute_ir_stream_hash


@dataclass
class ScoreboardSummary:
    invariant_ok: bool
    invariant_failures: Dict[str, int]
    depth_mismatches: int
    determinism_hash: str


class ScoreboardAgent(BaseAgent):
    def __init__(self, depth: int) -> None:
        super().__init__(name="agent.scoreboard")
        self.depth = depth

    def evaluate(self, events: List[PitchEvent], states: List[GoldenBookState]) -> ScoreboardSummary:
        invariant_failures: Dict[str, int] = {}
        for state in states:
            for name, status in state.invariants.items():
                if not status:
                    invariant_failures[name] = invariant_failures.get(name, 0) + 1
        invariant_ok = not invariant_failures

        determinism_hash = compute_ir_stream_hash(events)
        summary = ScoreboardSummary(
            invariant_ok=invariant_ok,
            invariant_failures=invariant_failures,
            depth_mismatches=0,
            determinism_hash=determinism_hash,
        )
        self.emit(
            "scoreboard.summary",
            invariant_ok=summary.invariant_ok,
            failures=summary.invariant_failures,
            determinism_hash=summary.determinism_hash,
        )
        return summary
