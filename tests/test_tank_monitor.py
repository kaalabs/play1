import pytest

from firmware.core.tank_monitor import TankMonitor


class FakeTankLevel:
    def __init__(self, seq):
        self.seq = list(seq)

    def read_level_percent(self):
        if not self.seq:
            return None
        return self.seq.pop(0)


def test_tank_monitor_hysteresis_transitions():
    # Sequence exercises ok -> critical -> low -> ok with hysteresis
    # Config defaults: low=20, crit=5, h=2
    tl = FakeTankLevel([25.0, 4.0, 6.0, 10.0, 23.0])
    tm = TankMonitor(tl)

    tm.sample()
    assert tm.level_pct == 25.0 and tm.state == "ok" and tm.tank_ok is True

    tm.sample()
    assert tm.state == "critical" and tm.tank_ok is False

    tm.sample()  # 6.0 < crit+h (7.0) stays critical
    assert tm.state == "critical"

    tm.sample()  # 10.0 -> above crit+h, becomes low
    assert tm.state == "low" and tm.tank_ok is False

    tm.sample()  # 23.0 -> above low+h (22.0), becomes ok
    assert tm.state == "ok" and tm.tank_ok is True


def test_tank_monitor_unknown_on_none():
    tl = FakeTankLevel([None])
    tm = TankMonitor(tl)
    tm.sample()
    assert tm.state == "unknown" and tm.tank_ok is False
