"""Field extractors for synthetic PITCH messages."""
from __future__ import annotations

from typing import Dict

from .binary_decoder import BinaryDecoder


FIELD_MAP = {
    "seq": "read_uint32",
    "ts_ns": "read_uint64",
    "msg_type": "read_char",
    "side": "read_char",
    "price": "read_uint32",
    "qty": "read_uint32",
    "order_id": "read_uint32",
    "unit": "read_uint16",
}


def extract_fields(decoder: BinaryDecoder) -> Dict[str, int | str]:
    result: Dict[str, int | str] = {}
    for field in ("seq", "ts_ns", "msg_type", "side", "price", "qty", "order_id", "unit"):
        reader = getattr(decoder, FIELD_MAP[field])
        result[field] = reader()
    return result
