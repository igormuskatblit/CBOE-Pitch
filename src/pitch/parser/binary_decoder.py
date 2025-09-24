"""Binary decoder using zero-copy memoryview slices."""
from __future__ import annotations

import struct
from dataclasses import dataclass


@dataclass
class BinaryDecoder:
    payload: bytes

    def __post_init__(self) -> None:
        self._view = memoryview(self.payload)
        self.offset = 0

    def at_end(self) -> bool:
        return self.offset >= len(self._view)

    def read_uint32(self) -> int:
        value = struct.unpack_from(">I", self._view, self.offset)[0]
        self.offset += 4
        return value

    def read_uint64(self) -> int:
        value = struct.unpack_from(">Q", self._view, self.offset)[0]
        self.offset += 8
        return value

    def read_uint16(self) -> int:
        value = struct.unpack_from(">H", self._view, self.offset)[0]
        self.offset += 2
        return value

    def read_char(self) -> str:
        value = struct.unpack_from(">c", self._view, self.offset)[0]
        self.offset += 1
        return value.decode("ascii")

    def slice(self, start: int, end: int) -> bytes:
        return self._view[start:end].tobytes()

    def advance(self, amount: int) -> None:
        self.offset = min(len(self._view), self.offset + amount)
