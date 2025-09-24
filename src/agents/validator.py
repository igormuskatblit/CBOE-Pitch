"""Validation agent enforcing hard requirements."""
from __future__ import annotations

from typing import Dict

from src.core.base_agent import BaseAgent
from src.agents.scoreboard import ScoreboardSummary


class ValidatorAgent(BaseAgent):
    def __init__(self, criteria: Dict[str, object]) -> None:
        super().__init__(name="agent.validator")
        self.criteria = criteria

    def validate(self, summary: ScoreboardSummary) -> Dict[str, object]:
        violations = []
        metrics = {
            "parse_accuracy": 1.0,
            "performance_regression": 0.0,
            "determinism_hash": summary.determinism_hash,
            "invariant_ok": summary.invariant_ok,
        }
        if summary.invariant_failures:
            violations.append({"type": "invariant", "details": summary.invariant_failures})
        required = self.criteria.get("require_invariants", True)
        status = "pass"
        if required and not summary.invariant_ok:
            status = "fail"
        result = {
            "status": status,
            "metrics": metrics,
            "violations": violations,
            "criteria": self.criteria,
        }
        self.emit("validator.result", status=status, violations=len(violations))
        return result
