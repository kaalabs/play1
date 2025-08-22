"""MicroPython entrypoint for Boiler Node.
Wire up HAL and BoilerController and run periodic control loop.
"""

import time
from firmware.core.hal_mpy import HAL
from firmware.core.boiler_controller import BoilerController


def main():
    hal = HAL()
    ctrl = BoilerController(hal)
    while True:
        now = time.time()
        p = hal.pressure_bar()
        # Autofill coordination is decentralized; if a shared signal exists, read it here.
        state, reason = ctrl.tick(now_s=now, p_bar=p, autofill_active=False)
        # Optional: minimal status LED or UART log
        hal.sleep_ms(200)


if __name__ == "__main__":
    main()
