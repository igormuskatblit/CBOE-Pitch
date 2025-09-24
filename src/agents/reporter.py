"""Reporter agent writing structured outputs."""
from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Dict

from src.core.base_agent import BaseAgent
from src.utils.hash_utils import compute_code_hash


class ReporterAgent(BaseAgent):
    def __init__(self, output_dir: Path) -> None:
        super().__init__(name="agent.reporter")
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "run_manifest.json"
        self.report_path = self.output_dir / "validation_report.json"

    def report(
        self,
        validation_result: Dict[str, object],
        scoreboard_result: object,
        config_hash: str,
        event_hash: str,
        demo_failure: bool,
    ) -> Dict[str, object]:
        payload = {
            "validation": validation_result,
            "scoreboard": {
                "invariant_ok": getattr(scoreboard_result, "invariant_ok", False),
                "invariant_failures": getattr(scoreboard_result, "invariant_failures", {}),
                "determinism_hash": getattr(scoreboard_result, "determinism_hash", ""),
            },
            "metadata": {
                "demo_failure": demo_failure,
            },
        }
        self._write_json(self.report_path, payload)

        manifest = {
            "before_event_hash": event_hash,
            "after_event_hash": event_hash,
            "cfg_hash_before": config_hash,
            "cfg_hash_after": config_hash,
            "code_hash": compute_code_hash(Path("src")),
            "tool_versions": {
                "python": platform.python_version(),
            },
        }
        self._write_json(self.manifest_path, manifest)
        self.emit("reporter.written", report=str(self.report_path), manifest=str(self.manifest_path))
        return payload

    def update_manifest_self_improve(self, payload: Dict[str, object]) -> None:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["self_improvement"] = payload.get("self_improvement", {})
        self._write_json(self.manifest_path, manifest)

    def _write_json(self, path: Path, payload: Dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
