"""MicroPython entrypoint for Autofill Node."""

from firmware.core.hal_mpy import HAL
from firmware.core.autofill_controller import AutofillController
from firmware.core.tank_monitor import TankMonitor
import time


def main():
    hal = HAL()
    tank = TankMonitor()
    ctrl = AutofillController(hal)
    while True:
        now = time.time()
        tank.sample()
        wet = hal.probe_wet()
        ctrl.tick(now_s=now, probe_wet=wet, tank_ok=tank.tank_ok)
        hal.sleep_ms(100)


if __name__ == "__main__":
    main()
