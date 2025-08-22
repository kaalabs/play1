"""MicroPython entrypoint for Autofill Node."""

from firmware.core.hal_mpy import HAL
from firmware.core.autofill_controller import AutofillController
import time


def main():
    hal = HAL()
    ctrl = AutofillController(hal)
    while True:
        now = time.time()
        wet = hal.probe_wet()
        ctrl.tick(now_s=now, probe_wet=wet)
        hal.sleep_ms(100)


if __name__ == "__main__":
    main()
