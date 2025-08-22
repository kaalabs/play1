# Boiler Controller: pressure-based hysteresis with safety interlocks
# Runs as an autonomous node on ESP32-WROOM-32E

from firmware.common import config
from firmware.common.safety import FaultLatch, Watchdog


class BoilerController:
    def __init__(self, hal, cfg: config.BoilerConfig = config.boiler):
        self.cfg = cfg
        self.hal = hal
        self.latch = FaultLatch()
        self.wd = Watchdog(timeout_s=2.0)
        self._heater_on = False
        self._last_on_time = 0.0
        self._last_off_time = 0.0

    def _plausibility(self, p_bar: float) -> bool:
        return self.cfg.sensor_min_bar <= p_bar <= self.cfg.sensor_max_bar

    def _safe_off(self):
        self.hal.heater(False)
        self._heater_on = False

    def tick(self, now_s: float, p_bar: float, autofill_active: bool = False):
        """Advance control one cycle.
        Returns (state, reason) where state in {heat, idle, hold, inhibit, fault}.
        """
        self.wd.kick()
        # Watchdog
        if self.wd.expired():
            self.latch.trip("watchdog_expired")

        if self.latch.tripped:
            self._safe_off()
            return "fault", self.latch.reason

        # Sensor plausibility
        if not self._plausibility(p_bar):
            self.latch.trip("sensor_out_of_range")
            self._safe_off()
            return "fault", self.latch.reason

        # Autofill interlock: do not heat during fill
        if autofill_active:
            self._safe_off()
            return "inhibit", "autofill"

        target = self.cfg.target_bar
        hyster = self.cfg.hysteresis_bar

        # Safety timeout on continuous ON
        if self._heater_on and (now_s - self._last_on_time) > self.cfg.max_continuous_on_s:
            self.latch.trip("heater_on_timeout")
            self._safe_off()
            return "fault", self.latch.reason

        # Control logic
        if p_bar < (target - hyster):
            # Respect minimum off recovery
            if (now_s - self._last_off_time) >= self.cfg.min_off_recovery_s:
                self.hal.heater(True)
                if not self._heater_on:
                    self._heater_on = True
                    self._last_on_time = now_s
            state = "heat"
        elif p_bar > (target + hyster):
            self._safe_off()
            self._last_off_time = now_s
            state = "idle"
        else:
            # inside band: hold state, but ensure hardware state matches
            self.hal.heater(self._heater_on)
            state = "hold" if self._heater_on else "idle"

        return state, None
