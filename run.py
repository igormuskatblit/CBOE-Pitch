"""CLI orchestrator for the PITCH verification framework."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

from src.core.agent_bus import AgentBus
from src.core.state_manager import StateManager
from src.utils.logging_config import configure_logging
from src.utils.hash_utils import compute_ir_stream_hash, compute_config_hash
from src.utils.simple_yaml import load_yaml
from src.agents.test_synthesizer import TestSynthesizer
from src.agents.time_seq_agent import TimeSequenceAgent
from src.agents.scoreboard import ScoreboardAgent
from src.agents.validator import ValidatorAgent
from src.agents.reporter import ReporterAgent
from src.agents.failure_miner import FailureMiner
from src.agents.test_generalizer import TestGeneralizer
from src.agents.patch_proposer import PatchProposer
from src.agents.patch_applier import PatchApplier
from src.agents.safety_gater import SafetyGater
from src.pitch.golden_book import GoldenBook
from src.pitch.parser import parse_messages

CONFIG_DIR = Path("config")
ARTIFACT_DIR = Path("artifacts") / "validation_results"
TEST_DATA_DIR = Path("test_data") / "synthetic"


def save_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def orchestrate(demo_failure: bool = False) -> Dict[str, object]:
    configure_logging()
    logger = logging.getLogger("run")
    policies = load_yaml(CONFIG_DIR / "policies.yaml")
    validation_criteria = load_yaml(CONFIG_DIR / "validation_criteria.yaml")

    bus = AgentBus()
    state = StateManager()
    synthesizer = TestSynthesizer(output_dir=TEST_DATA_DIR)

    vector = synthesizer.generate_failure_sequence() if demo_failure else synthesizer.generate_basic_sequence()
    logger.info("vector.generated", extra={"vector_name": vector.name})

    events = parse_messages(vector.payload, parser_version="0.1.0")
    state.set("events_raw", events)

    time_agent = TimeSequenceAgent(policies=policies.get("time_sequence", {}))
    normalized_events = time_agent.normalize(events)
    state.set("events_normalized", normalized_events)

    golden = GoldenBook(depth=int(policies.get("golden_book", {}).get("depth", 5)))
    golden_states = golden.process_events(normalized_events)
    state.set("golden_states", golden_states)

    scoreboard = ScoreboardAgent(depth=int(policies.get("scoreboard", {}).get("depth", 5)))
    scoreboard_result = scoreboard.evaluate(normalized_events, golden_states)
    state.set("scoreboard_result", scoreboard_result)

    validator = ValidatorAgent(criteria=validation_criteria)
    validation_result = validator.validate(scoreboard_result)
    state.set("validation_result", validation_result)

    reporter = ReporterAgent(output_dir=ARTIFACT_DIR)
    reporter_payload = reporter.report(
        validation_result=validation_result,
        scoreboard_result=scoreboard_result,
        config_hash=compute_config_hash(CONFIG_DIR),
        event_hash=compute_ir_stream_hash(normalized_events),
        demo_failure=demo_failure,
    )
    state.set("report", reporter_payload)

    if demo_failure and not scoreboard_result.invariant_ok:
        failure_miner = FailureMiner(output_dir=TEST_DATA_DIR)
        mre_path = failure_miner.mine(normalized_events, scoreboard_result)

        generalizer = TestGeneralizer(output_dir=TEST_DATA_DIR)
        generalized_path = generalizer.generalize(mre_path)

        proposer = PatchProposer()
        patch_proposal = proposer.propose(scoreboard_result, validation_result)
        state.set("patch_proposal", patch_proposal)

        applier = PatchApplier(config_path=CONFIG_DIR / "policies.yaml")
        patch_result = applier.apply_patch(patch_proposal)
        state.set("patch_result", patch_result)

        gater = SafetyGater()
        gate_result = gater.assess(scoreboard_result, patch_result)
        state.set("gate_result", gate_result)

        reporter_payload["self_improvement"] = {
            "mre_path": str(mre_path),
            "generalized_path": str(generalized_path),
            "patch_proposal": patch_proposal,
            "patch_result": patch_result,
            "gate_result": gate_result,
        }
        reporter.update_manifest_self_improve(reporter_payload)

    return reporter_payload


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the PITCH verification pipeline")
    parser.add_argument("--demo-failure", action="store_true", help="Trigger a demo failure and self-improvement loop")
    args = parser.parse_args(argv)

    try:
        orchestrate(demo_failure=args.demo_failure)
    except Exception as exc:  # noqa: BLE001
        logging.getLogger("run").exception("pipeline.failed", extra={"error": str(exc)})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
