"""Deterministic synthetic test vector generator."""
from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from src.core.base_agent import BaseAgent


@dataclass(slots=True)
class TestVector:
    name: str
    payload: bytes
    metadata: Dict[str, object]


class TestSynthesizer(BaseAgent):
    def __init__(self, output_dir: Path) -> None:
        super().__init__(name="agent.test_synthesizer")
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _pack(self, seq: int, ts_ns: int, msg_type: str, side: str, price: int, qty: int, order_id: int, unit: int) -> bytes:
        return struct.pack(
            ">IQccIIIH",
            seq,
            ts_ns,
            msg_type.encode("ascii"),
            side.encode("ascii"),
            price,
            qty,
            order_id,
            unit,
        )

    def generate_basic_sequence(self) -> TestVector:
        self.emit("vector.basic.start")
        messages = [
            self._pack(1, 100, "A", "B", 10000, 10, 1, 1),
            self._pack(2, 200, "A", "S", 10050, 10, 2, 1),
            self._pack(3, 300, "E", "B", 10000, 5, 1, 1),
            self._pack(4, 400, "D", "S", 10050, 0, 2, 1),
        ]
        payload = b"".join(messages)
        vector = TestVector(name="basic_pass", payload=payload, metadata={"size": len(payload)})
        self._persist(vector)
        return vector

    def generate_failure_sequence(self) -> TestVector:
        self.emit("vector.failure.start")
        messages = [
            self._pack(1, 100, "A", "B", 10100, 10, 10, 1),
            self._pack(2, 200, "A", "S", 10000, 10, 11, 1),
            self._pack(3, 300, "A", "B", 9900, 10, 12, 1),
        ]
        payload = b"".join(messages)
        vector = TestVector(name="crossed_book", payload=payload, metadata={"size": len(payload)})
        self._persist(vector)
        return vector

    def _persist(self, vector: TestVector) -> None:
        path = self.output_dir / f"{vector.name}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump({"name": vector.name, "size": vector.metadata["size"]}, handle)
        self.emit("vector.persisted", path=str(path))
