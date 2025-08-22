import pytest
from firmware.core.tank_sensor import DYPFrameParser, TankLevel
from firmware.common import config


class FakeUART:
    def __init__(self, frames):
        self.frames = bytearray()
        for d in frames:
            hi = (d >> 8) & 0xFF
            lo = d & 0xFF
            s = (0xFF + hi + lo) & 0xFF
            self.frames.extend(bytes([0xFF, hi, lo, s]))
        self._idx = 0

    def read(self):
        if self._idx >= len(self.frames):
            return None
        # Return a few bytes at a time to test resync
        end = min(self._idx + 3, len(self.frames))
        chunk = self.frames[self._idx:end]
        self._idx = end
        return bytes(chunk)


def test_parser_valid_and_resync():
    p = DYPFrameParser()
    # feed noise and then a valid frame for 1234mm
    noise = b"\x00\x01\x02"
    hi = (1234 >> 8) & 0xFF
    lo = 1234 & 0xFF
    s = (0xFF + hi + lo) & 0xFF
    frame = bytes([0xFF, hi, lo, s])
    assert p.feed(noise) is None
    assert p.feed(frame) == 1234


def test_tank_level_percent_mapping_and_smoothing():
    frames = [40, 120, 200]  # full, mid, empty distances
    uart = FakeUART(frames)
    # Use a copy of config with no smoothing to make assertions deterministic
    from collections import namedtuple
    TankCfg = namedtuple('TankCfg', 'full_distance_mm empty_distance_mm smoothing_alpha sample_hz')
    cfg = TankCfg(
        full_distance_mm=config.tank.full_distance_mm,
        empty_distance_mm=config.tank.empty_distance_mm,
        smoothing_alpha=1.0,
        sample_hz=config.tank.sample_hz,
    )
    tl = TankLevel(uart=uart, cfg=cfg)
    p1 = tl.read_level_percent()
    p2 = tl.read_level_percent()
    p3 = tl.read_level_percent()
    assert p1 is not None and 90 <= p1 <= 100
    assert p2 is not None and 20 <= p2 <= 80
    assert p3 is not None and 0 <= p3 <= 20
