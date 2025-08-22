"""Master-side tank level service and simple serial RPC.

Provides:
- Periodic read of TankLevel
- Alert state with hysteresis
- Minimal line-based RPC over stdin/stdout for integration or debugging:
  - "get_level" -> {"level_pct": float|null, "state": "ok|low|critical|unknown"}
"""

import json
import sys
import time
from typing import Optional

from firmware.core.tank_sensor import TankLevel
from firmware.common import config


class TankAlerts:
    def __init__(self, cfg=config.tank):
        self.cfg = cfg
        self.state = "unknown"  # ok|low|critical|unknown

    def update(self, level_pct: Optional[float]) -> str:
        if level_pct is None:
            self.state = "unknown"
            return self.state
        low = self.cfg.low_pct
        crit = self.cfg.critical_pct
        h = self.cfg.hysteresis_pct

        s = self.state
        if s in ("unknown", "ok"):
            if level_pct <= crit:
                s = "critical"
            elif level_pct <= low:
                s = "low"
            else:
                s = "ok"
        elif s == "low":
            if level_pct <= crit:
                s = "critical"
            elif level_pct >= low + h:
                s = "ok"
        elif s == "critical":
            if level_pct >= crit + h:
                # can move up to low or ok depending on value
                s = "low" if level_pct <= low else "ok"
        self.state = s
        return s


def handle_cmd(cmd: str, level_cache, alerts: TankAlerts):
    if cmd == "get_level":
        return {"level_pct": level_cache, "state": alerts.state}
    return {"error": "unknown_cmd"}


def rpc_loop(sample_period_s: float = 0.2):
    tank = TankLevel()
    alerts = TankAlerts()
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
    out = handle_cmd(cmd, level_cache, alerts)
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    rpc_loop()
