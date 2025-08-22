"""Minimal Modbus RTU helpers for MicroPython nodes.

Provides:
- CRC16 (Modbus) calculator
- RTU PDU/ADU helpers (build, parse)
- Simple, non-blocking slave that serves a user-provided register map

This is intentionally tiny and synchronous to keep footprint small.
"""

from typing import Callable, Dict, Tuple, Optional


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    crc &= 0xFFFF
    # Return in high-byte-first numeric form (e.g., 0xC5CD for [0xCD, 0xC5])
    return ((crc & 0xFF) << 8) | (crc >> 8)


def build_adu(addr: int, pdu: bytes) -> bytes:
    adu = bytes([addr]) + pdu
    # Compute raw LSB-first word for wire by swapping numeric
    c = crc16(adu)
    c_lsb_first = ((c & 0xFF) << 8) | (c >> 8)
    return adu + bytes([c_lsb_first & 0xFF, (c_lsb_first >> 8) & 0xFF])


def check_and_strip_adu(frame: bytes) -> Tuple[int, bytes]:
    if len(frame) < 4:
        raise ValueError("short_frame")
    addr = frame[0]
    data = frame[:-2]
    rx_crc_le = frame[-2] | (frame[-1] << 8)
    # Convert to big-endian numeric like crc16() returns
    rx_crc_be = ((rx_crc_le & 0xFF) << 8) | (rx_crc_le >> 8)
    if crc16(data) != rx_crc_be:
        raise ValueError("bad_crc")
    return addr, frame[1:-2]


class SimpleSlave:
    """Tiny Modbus RTU slave. Handles 0x03 (Read Holding), 0x06 (Write Single), 0x10 (Write Multiple).

    reg_read: Callable[[int, int], Tuple[bool, Tuple[int, ...]]]
      Given (start, count) -> (ok, values)
    reg_write: Callable[[int, Tuple[int, ...]], bool]
      Given (start, values) -> ok
    """

    def __init__(self, addr: int, read_cb: Callable[[int, int], Tuple[bool, Tuple[int, ...]]], write_cb: Callable[[int, Tuple[int, ...]], bool]):
        self.addr = addr
        self.read_cb = read_cb
        self.write_cb = write_cb
        self._buf = bytearray()

    def _exception(self, func: int, code: int) -> bytes:
        return build_adu(self.addr, bytes([func | 0x80, code]))

    def _handle_pdu(self, pdu: bytes) -> bytes:
        func = pdu[0]
        if func == 0x03:  # Read Holding Registers
            if len(pdu) != 5:
                return self._exception(func, 0x03)
            start = (pdu[1] << 8) | pdu[2]
            count = (pdu[3] << 8) | pdu[4]
            ok, vals = self.read_cb(start, count)
            if not ok:
                return self._exception(func, 0x02)
            if len(vals) != count:
                return self._exception(func, 0x03)
            by = bytearray([func, count * 2])
            for v in vals:
                by.append((v >> 8) & 0xFF)
                by.append(v & 0xFF)
            return build_adu(self.addr, bytes(by))
        elif func == 0x06:  # Write Single Register
            if len(pdu) != 5:
                return self._exception(func, 0x03)
            start = (pdu[1] << 8) | pdu[2]
            val = (pdu[3] << 8) | pdu[4]
            ok = self.write_cb(start, (val,))
            if not ok:
                return self._exception(func, 0x02)
            return build_adu(self.addr, pdu)
        elif func == 0x10:  # Write Multiple
            if len(pdu) < 6:
                return self._exception(func, 0x03)
            start = (pdu[1] << 8) | pdu[2]
            count = (pdu[3] << 8) | pdu[4]
            nbytes = pdu[5]
            if nbytes != count * 2 or len(pdu) != 6 + nbytes:
                return self._exception(func, 0x03)
            vals = []
            i = 6
            for _ in range(count):
                vals.append((pdu[i] << 8) | pdu[i + 1])
                i += 2
            ok = self.write_cb(start, tuple(vals))
            if not ok:
                return self._exception(func, 0x02)
            # Echo start & count
            return build_adu(self.addr, bytes([func, (start >> 8) & 0xFF, start & 0xFF, (count >> 8) & 0xFF, count & 0xFF]))
        else:
            return self._exception(func, 0x01)

    def feed_uart(self, data: bytes) -> Optional[bytes]:
        """Feed raw UART bytes; returns a response ADU or None if incomplete/ignored.
        Caller is responsible for turnaround timing (DE toggling) and inter-frame gap if needed.
        """
        self._buf.extend(data)
        # Try to find a complete frame (we assume clean frame boundaries or single frame bursts)
        if len(self._buf) < 4:
            return None
        # Attempt CRC check on current buffer; if bad, drop first byte and resync
        try:
            addr, pdu = check_and_strip_adu(bytes(self._buf))
        except ValueError:
            self._buf = self._buf[1:]
            return None
        self._buf.clear()
        if addr != self.addr:
            return None
        return self._handle_pdu(pdu)
