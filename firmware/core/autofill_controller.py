# Autofill Controller: manages boiler level probe and fill valve interlocks

from firmware.common import config
from firmware.common.safety import FaultLatch, Watchdog


class AutofillController:
    def __init__(self, hal, cfg: config.AutofillConfig = config.autofill):
        self.cfg = cfg
        self.hal = hal
        self.latch = FaultLatch()
        self.wd = Watchdog(timeout_s=2.0)
        self._fill_active = False
        self._fill_start_s = 0.0
        self._last_fill_end_s = -1e9

    def tick(self, now_s: float, probe_wet: bool, tank_ok: bool = True):
        self.wd.kick()
        if self.wd.expired():
            self.latch.trip("watchdog_expired")

        if self.latch.tripped:
            self.hal.fill_valve(False)
            self._fill_active = False
            return "fault", self.latch.reason

        # Debounced semantics handled by higher layer or HAL conditioning assumed
        # Tank interlock: never autofill if tank is not OK
        if not tank_ok:
            self.hal.fill_valve(False)
            self._fill_active = False
            return "inhibit", "tank_not_ok"

        if probe_wet:
            # Level OK
            if self._fill_active:
                self.hal.fill_valve(False)
                self._fill_active = False
                self._last_fill_end_s = now_s
            return "ok", None
        else:
            # Level low; check rate limiting
            if (now_s - self._last_fill_end_s) < self.cfg.min_refill_interval_s:
                self.hal.fill_valve(False)
                self._fill_active = False
                return "inhibit", "rate_limit"

            # Start or continue fill
            if not self._fill_active:
                self._fill_active = True
                self._fill_start_s = now_s
            self.hal.fill_valve(True)

            # Timeout safety
            if (now_s - self._fill_start_s) > self.cfg.fill_timeout_s:
                self.latch.trip("fill_timeout")
                self.hal.fill_valve(False)
                self._fill_active = False
                return "fault", self.latch.reason

            return "fill", None
