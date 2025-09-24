"""Safety gate evaluating patch efficacy."""
from __future__ import annotations

from typing import Dict

from src.core.base_agent import BaseAgent
from src.agents.scoreboard import ScoreboardSummary


class SafetyGater(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="agent.safety_gater")

    def assess(self, summary: ScoreboardSummary, patch_result: Dict[str, object]) -> Dict[str, object]:
        accepted = False
        reason = ""
        if patch_result.get("status") != "patched":
            reason = "no change applied"
        elif summary.invariant_ok:
            accepted = True
            reason = "no outstanding failures"
        else:
            reason = "invariants still failing"
        decision = {"accepted": accepted, "reason": reason}
        self.emit("safety.gate", accepted=accepted, reason=reason)
        return decision
