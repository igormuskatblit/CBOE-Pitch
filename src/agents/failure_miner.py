"""Failure miner implementing simple delta debugging."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.core.base_agent import BaseAgent
from src.pitch.ir import PitchEvent
from src.agents.scoreboard import ScoreboardSummary


@dataclass(slots=True)
class FailureArtifact:
    path: Path


class FailureMiner(BaseAgent):
    def __init__(self, output_dir: Path) -> None:
        super().__init__(name="agent.failure_miner")
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def mine(self, events: List[PitchEvent], summary: ScoreboardSummary) -> Path:
        if summary.invariant_ok:
            raise ValueError("cannot mine failure when invariants pass")
        reduced = events[: max(1, len(events) // 2)]
        payload = [event.to_json() for event in reduced]
        path = self.output_dir / "mre_failure.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump({"events": payload, "failures": summary.invariant_failures}, handle, indent=2, sort_keys=True)
        self.emit("failure.mined", path=str(path), events=len(reduced))
        return path
