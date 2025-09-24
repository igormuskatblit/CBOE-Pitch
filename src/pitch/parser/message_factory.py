"""Synthetic message factory."""
from __future__ import annotations

from typing import Dict

from .field_extractors import extract_fields
from .binary_decoder import BinaryDecoder


def build_message(decoder: BinaryDecoder) -> Dict[str, int | str]:
    fields = extract_fields(decoder)
    return {
        "seq": int(fields["seq"]),
        "ts_ns": int(fields["ts_ns"]),
        "msg_type": str(fields["msg_type"]),
        "side": str(fields["side"]),
        "price": int(fields["price"]),
        "qty": int(fields["qty"]),
        "order_id": int(fields["order_id"]),
        "unit": int(fields["unit"]),
    }
