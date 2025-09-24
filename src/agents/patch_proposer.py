"""Patch proposer producing minimal config deltas."""
from __future__ import annotations

from typing import Dict

from src.core.base_agent import BaseAgent
from src.agents.scoreboard import ScoreboardSummary


class PatchProposer(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="agent.patch_proposer")

    def propose(self, summary: ScoreboardSummary, validation_result: Dict[str, object]) -> Dict[str, object]:
        proposal = {
            "target": "config/policies.yaml",
            "changes": {"scoreboard": {"depth": 10}},
            "rationale": "increase depth to capture crossed-book scenarios",
            "rollback": "restore previous scoreboard.depth",
        }
        if summary.invariant_ok:
            proposal["changes"] = {}
            proposal["rationale"] = "no change required"
        self.emit("patch.proposed", accepted=not summary.invariant_ok)
        return proposal
