"""DYP-A02YYUW ultrasonic tank level sensor driver.

Sensor sends 4-byte frames at ~10Hz via UART (TTL): 0xFF, 0xXX, 0xYY, sum.
Distance (mm) = 256 * XX + YY, valid range ~30..4500.

We parse frames with resynchronization and expose level percent using config thresholds.
"""

from typing import Optional
from firmware.common import config

try:
    from machine import UART
    MICROPY = True
except ImportError:  # allow import under CPython for tests/tools
    UART = object  # type: ignore
    MICROPY = False


class DYPFrameParser:
    def __init__(self):
        self._buf = bytearray()

    def feed(self, data: bytes) -> Optional[int]:
        """Feed bytes, return distance_mm if a valid frame is parsed else None."""
        self._buf.extend(data)
        # Attempt to parse frames from buffer
        while len(self._buf) >= 4:
            # sync to 0xFF
            if self._buf[0] != 0xFF:
                # drop until 0xFF
                del self._buf[0]
                continue
            frame = self._buf[:4]
            s = (frame[0] + frame[1] + frame[2]) & 0xFF
            if frame[3] != s:
                # bad checksum, drop first byte
                del self._buf[0]
                continue
            # valid frame
            dist = frame[1] * 256 + frame[2]
            # pop frame
            del self._buf[:4]
            if 30 <= dist <= 4500:
                return dist
            # else ignore out-of-range and continue
        return None


class TankLevel:
    def __init__(self, uart=None, cfg: config.TankLevelConfig = config.tank):
        self.cfg = cfg
        self.uart = uart
        self.parser = DYPFrameParser()
        self._ema = None

        if self.uart is None and MICROPY:
            # Initialize UART from pins
            pins = config.pins
            try:
                self.uart = UART(
                    pins.tank_uart_id,
                    baudrate=9600,
                    tx=pins.tank_uart_tx,
                    rx=pins.tank_uart_rx,
                    timeout=100,
                )
            except Exception:
                self.uart = None

    def _read_distance_mm(self) -> Optional[int]:
        if not self.uart:
            return None
        # Try a few reads to handle partial frames
        for _ in range(8):
            try:
                data = self.uart.read()
            except Exception:
                data = None
            if not data:
                continue
            dist = self.parser.feed(data)
            if dist is not None:
                return dist
        return None

    def _distance_to_percent(self, dist_mm: int) -> float:
        full_d = float(self.cfg.full_distance_mm)
        empty_d = float(self.cfg.empty_distance_mm)
        if empty_d <= full_d:
            return 0.0
        # Map full->0mm gap to 100%, empty->bigger gap to 0%
        pct = (empty_d - dist_mm) / (empty_d - full_d)
        return max(0.0, min(1.0, pct)) * 100.0

    def read_level_percent(self) -> Optional[float]:
        d = self._read_distance_mm()
        if d is None:
            return None
        pct = self._distance_to_percent(d)
        a = self.cfg.smoothing_alpha
        if self._ema is None:
            self._ema = pct
        else:
            self._ema = a * pct + (1 - a) * self._ema
        return self._ema
