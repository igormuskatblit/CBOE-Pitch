"""PCAP processor stub.

This agent documents how a production implementation would decode PCAP files
without relying on external libraries. The pure-python backend is intentionally
minimal and only demonstrates interface compliance."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from src.core.base_agent import BaseAgent


class PCAPProcessor(BaseAgent):
    """Stub processor that returns raw frames as bytes."""

    def __init__(self) -> None:
        super().__init__(name="agent.pcap_processor")

    def read(self, path: Path) -> List[bytes]:
        self.emit("pcap.read", path=str(path))
        if not path.exists():
            return []
        # Production implementation would parse PCAP headers; here we simply
        # chunk the file to demonstrate streaming behaviour.
        data = path.read_bytes()
        frame_size = max(1, len(data) // 4)
        frames = [data[i : i + frame_size] for i in range(0, len(data), frame_size)]
        return frames
