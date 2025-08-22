"""Autonomous Tank Monitor

Runs on a core node to determine if the water tank is OK for operation.
It wraps TankLevel (ultrasonic) and applies hysteresis thresholds to
produce a tri-state: ok | low | critical | unknown, plus a tank_ok bool.

This is used to interlock Pump and Autofill locally, removing any
dependency on a master UX.
"""

from typing import Optional

from firmware.common import config
from firmware.core.tank_sensor import TankLevel


class TankMonitor:
    def __init__(self, tl: Optional[TankLevel] = None, cfg: config.TankLevelConfig = config.tank):
        self.cfg = cfg
        self.tl = tl or TankLevel()
        self.state: str = "unknown"  # ok|low|critical|unknown
        self.level_pct: Optional[float] = None

    def _apply_hysteresis(self, level_pct: Optional[float]) -> str:
        if level_pct is None:
            return "unknown"
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
                s = "low" if level_pct <= low else "ok"
        return s

    def sample(self) -> None:
        """Read the current level percent and update state."""
        self.level_pct = self.tl.read_level_percent()
        self.state = self._apply_hysteresis(self.level_pct)

    @property
    def tank_ok(self) -> bool:
        """True only when the tank state is ok."""
        return self.state == "ok"
