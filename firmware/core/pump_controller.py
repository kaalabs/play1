"""Pump/Brew Controller

Controls pump based on brew switch input with safety limits:
- Max continuous run time
- Min rest time between runs
- Starts-per-minute limit

Inputs: now_s (float), brew_switch (bool)
Outputs: pump actuator state via HAL
"""

from firmware.common import config
from firmware.common.safety import FaultLatch, Watchdog, RateLimiter


class PumpController:
    def __init__(self, hal, cfg: config.PumpConfig = config.pump):
        self.cfg = cfg
        self.hal = hal
        self.latch = FaultLatch()
        self.wd = Watchdog(timeout_s=2.0)

        self._pump_on = False
        self._run_start_s = 0.0
        self._last_stop_s = -1e9
        self._start_times = []  # timestamps of recent starts (for per-minute limit)

    def _enforce_limits_prestart(self, now_s: float):
        # Min rest between runs
        if (now_s - self._last_stop_s) < self.cfg.min_rest_s:
            return "inhibit", "rest"
        # Starts per minute
        window = 60.0
        self._start_times = [t for t in self._start_times if (now_s - t) <= window]
        if len(self._start_times) >= self.cfg.max_starts_per_min:
            return "inhibit", "rate_limit"
        return None, None

    def _safe_off(self):
        self.hal.pump(False)
        if self._pump_on:
            self._pump_on = False
            self._last_stop_s = self._last_time

    def tick(self, now_s: float, brew_switch: bool):
        self._last_time = now_s
        if self.wd.expired():
            self.latch.trip("watchdog_expired")

        if self.latch.tripped:
            self._safe_off()
            return "fault", self.latch.reason

        if not brew_switch:
            # command off
            self._safe_off()
            return "idle", None

        # command on
        if not self._pump_on:
            state, reason = self._enforce_limits_prestart(now_s)
            if state:
                self._safe_off()
                return state, reason
            # Start pump
            self.hal.pump(True)
            self._pump_on = True
            self._run_start_s = now_s
            self._start_times.append(now_s)
            return "run", None
        else:
            # already running, check run-time limit
            if (now_s - self._run_start_s) > self.cfg.max_run_s:
                self.latch.trip("pump_run_timeout")
                self._safe_off()
                return "fault", self.latch.reason
            self.hal.pump(True)
            return "run", None
