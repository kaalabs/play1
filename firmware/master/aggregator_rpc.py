"""Line-based RPC that aggregates tank and scale statuses.

Commands:
- get_status -> { tank:{level_pct,state}, scale:{weight_g,flow_gps,stable,source} }
"""

import json
import sys
import time
from typing import Optional

from .aggregator_service import get_status
from .scale_service import ScaleService
from .tank_service import TankAlerts
from firmware.core.tank_sensor import TankLevel


def rpc_loop(sample_period_s: float = 0.2):
    tank = TankLevel()
    alerts = TankAlerts()
    scale = ScaleService()
    last_sample = 0.0
    level_cache: Optional[float] = None
    while True:
        now = time.time()
        if now - last_sample >= sample_period_s:
            level_cache = tank.read_level_percent()
            alerts.update(level_cache)
            last_sample = now
        line = sys.stdin.readline()
        if not line:
            time.sleep(0.05)
            continue
        cmd = line.strip()
        if cmd == 'get_status':
            sr = scale.reading()
            out = get_status(level_pct=level_cache or 0.0, tank_state=alerts.state, weight_g=sr['weight_g'], stable=sr['stable'], source=sr['source'], flow_gps=sr['flow_gps'])
        else:
            out = {'error': 'unknown_cmd'}
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()


if __name__ == '__main__':
    rpc_loop()
