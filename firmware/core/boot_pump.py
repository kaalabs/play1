"""MicroPython entrypoint for Pump/Brew Node."""

import time
from firmware.core.hal_mpy import HAL
from firmware.core.pump_controller import PumpController


def main():
    hal = HAL()
    ctrl = PumpController(hal)
    while True:
        now = time.time()
        brew = hal.brew_switch()
        ctrl.tick(now_s=now, brew_switch=brew)
        hal.sleep_ms(50)


if __name__ == "__main__":
    main()
