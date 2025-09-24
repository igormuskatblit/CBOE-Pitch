"""Generalises failure traces into reusable templates."""
from __future__ import annotations

import json
from pathlib import Path

from src.core.base_agent import BaseAgent


class TestGeneralizer(BaseAgent):
    def __init__(self, output_dir: Path) -> None:
        super().__init__(name="agent.test_generalizer")
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generalize(self, mre_path: Path) -> Path:
        data = json.loads(mre_path.read_text(encoding="utf-8"))
        template = {
            "pattern": "crossed_book",
            "length": len(data.get("events", [])),
            "failures": data.get("failures", {}),
        }
        path = self.output_dir / "generalized_failure.json"
        path.write_text(json.dumps(template, indent=2, sort_keys=True), encoding="utf-8")
        self.emit("failure.generalized", path=str(path))
        return path
