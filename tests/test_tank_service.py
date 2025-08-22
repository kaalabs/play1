import json
import io
import sys
from contextlib import redirect_stdout

from firmware.master.tank_service import TankAlerts, handle_cmd


def test_alerts_hysteresis():
    cfg = type('Cfg', (), dict(low_pct=20.0, critical_pct=5.0, hysteresis_pct=2.0))
    ta = TankAlerts(cfg)
    assert ta.update(50.0) == 'ok'
    assert ta.update(10.0) == 'low'
    # small rise should stay low due to hysteresis
    # Need to exceed low+hysteresis to return to ok; at 21 stays low
    assert ta.update(21.0) == 'low'
    assert ta.update(22.1) == 'ok'
    assert ta.update(4.0) == 'critical'
    assert ta.update(7.1) == 'low'  # above crit+hyst but still below low


def test_handle_cmd_smoke():
    class DummyAlerts:
        state = 'ok'
    out = handle_cmd('get_level', 42.0, DummyAlerts())
    assert out['level_pct'] == 42.0
    assert out['state'] == 'ok'
    assert 'error' in handle_cmd('bogus', 0, DummyAlerts())
