"""Applies config patches with rollback support."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from src.core.base_agent import BaseAgent
from src.utils.simple_yaml import load_yaml, save_yaml


class PatchApplier(BaseAgent):
    def __init__(self, config_path: Path) -> None:
        super().__init__(name="agent.patch_applier")
        self.config_path = config_path

    def apply_patch(self, proposal: Dict[str, object]) -> Dict[str, object]:
        if not proposal.get("changes"):
            return {"status": "noop"}
        backup_path = self.config_path.with_suffix(self.config_path.suffix + ".bak")
        backup_path.write_text(self.config_path.read_text(encoding="utf-8"), encoding="utf-8")
        data = load_yaml(self.config_path)
        for section, changes in proposal["changes"].items():
            if section not in data:
                data[section] = {}
            if isinstance(changes, dict):
                data[section].update(changes)
        save_yaml(self.config_path, data)
        result = {
            "status": "patched",
            "backup": str(backup_path),
        }
        self.emit("patch.applied", status=result["status"], backup=str(backup_path))
        return result
