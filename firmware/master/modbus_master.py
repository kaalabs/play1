"""Simple Modbus RTU master (desktop CPython) using pyserial (optional).

For unit tests, we only rely on frame builders and leave serial optional.
"""

from typing import Tuple
from firmware.core.modbus_rtu import build_adu, crc16, check_and_strip_adu


def build_read_holding(addr: int, start: int, count: int) -> bytes:
    pdu = bytes([0x03, (start >> 8) & 0xFF, start & 0xFF, (count >> 8) & 0xFF, count & 0xFF])
    return build_adu(addr, pdu)


def parse_read_holding_response(frame: bytes) -> Tuple[int, Tuple[int, ...]]:
    addr, pdu = check_and_strip_adu(frame)
    if not pdu or pdu[0] != 0x03:
        raise ValueError("bad_func")
    n = pdu[1]
    if n % 2 != 0:
        raise ValueError("bad_len")
    vals = []
    i = 2
    while i < 2 + n:
        vals.append((pdu[i] << 8) | pdu[i + 1])
        i += 2
    return addr, tuple(vals)
