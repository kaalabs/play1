"""MicroPython entrypoint for Pump/Brew Node."""

import time
from firmware.core.hal_mpy import HAL
from firmware.core.pump_controller import PumpController
from firmware.core.tank_monitor import TankMonitor


def main():
    hal = HAL()
    tank = TankMonitor()
    ctrl = PumpController(hal)
    while True:
        now = time.time()
        tank.sample()
        brew = hal.brew_switch()
        ctrl.tick(now_s=now, brew_switch=brew, tank_ok=tank.tank_ok)
        hal.sleep_ms(50)


if __name__ == "__main__":
    main()
