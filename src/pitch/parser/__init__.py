"""Parser entry point."""
from __future__ import annotations

from typing import List

from .binary_decoder import BinaryDecoder
from .message_factory import build_message
from .validation_layer import validate_message
from .error_recovery import RecoveryContext
from ..ir import PitchEvent


def parse_messages(payload: bytes, parser_version: str) -> List[PitchEvent]:
    decoder = BinaryDecoder(payload)
    events: List[PitchEvent] = []
    recovery = RecoveryContext()
    while not decoder.at_end():
        offset = decoder.offset
        try:
            message = build_message(decoder)
            validate_message(message)
            events.append(
                PitchEvent(
                    seq=message["seq"],
                    unit=message["unit"],
                    ts_ns=message["ts_ns"],
                    msg_type=message["msg_type"],
                    raw=decoder.slice(offset, decoder.offset),
                    f={"price": message.get("price", 0), "qty": message.get("qty", 0)},
                    meta={
                        "parser_version": parser_version,
                        "byte_offset": offset,
                        "warnings": recovery.warnings[:],
                        "side": message.get("side"),
                        "order_id": message.get("order_id"),
                    },
                )
            )
            recovery.reset()
        except Exception as exc:  # noqa: BLE001
            recovery.record_failure(offset, str(exc))
            decoder.advance(1)
    return events
