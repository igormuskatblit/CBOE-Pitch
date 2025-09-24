"""Hash utilities for determinism guarantees."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, List

from src.pitch.ir import PitchEvent


def _hash_bytes(chunks: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    for chunk in chunks:
        digest.update(chunk)
    return digest.hexdigest()


def compute_ir_stream_hash(events: List[PitchEvent]) -> str:
    payload = []
    for event in events:
        payload.append(
            {
                "seq": event.seq,
                "unit": event.unit,
                "ts_ns": event.ts_ns,
                "msg_type": event.msg_type,
                "raw": event.raw.hex(),
                "f": event.f,
                "meta": event.meta,
            }
        )
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _hash_bytes([encoded])


def compute_config_hash(config_dir: Path) -> str:
    files = sorted(path for path in config_dir.rglob("*") if path.is_file())
    chunks = []
    for path in files:
        chunks.append(path.relative_to(config_dir).as_posix().encode("utf-8"))
        chunks.append(path.read_bytes())
    return _hash_bytes(chunks)


def compute_code_hash(root: Path) -> str:
    files = sorted(path for path in root.rglob("*.py") if path.is_file())
    chunks = []
    for path in files:
        chunks.append(path.relative_to(root).as_posix().encode("utf-8"))
        chunks.append(path.read_bytes())
    return _hash_bytes(chunks)
