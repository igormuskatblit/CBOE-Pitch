"""Validation checks for synthetic messages."""
from __future__ import annotations

from typing import Dict


def validate_message(message: Dict[str, int | str]) -> None:
    if message["seq"] <= 0:
        raise ValueError("sequence must be positive")
    if message["qty"] < 0:
        raise ValueError("quantity negative")
    if message["price"] < 0:
        raise ValueError("price negative")
    if message["msg_type"] not in {"A", "E", "D"}:
        raise ValueError("unsupported message type")
    if message["side"] not in {"B", "S"}:
        raise ValueError("unsupported side")
