"""MicroPython entrypoint for Boiler Node.
Wire up HAL and BoilerController and run periodic control loop.
"""

import time
from firmware.core.hal_mpy import HAL
from firmware.core.boiler_controller import BoilerController
from firmware.core.modbus_rtu import SimpleSlave
from firmware.core.modbus_maps import BoilerMap
from firmware.common import config
try:
    from machine import UART, Pin
except Exception:  # pragma: no cover
    UART = None
    Pin = None


def main():
    hal = HAL()
    ctrl = BoilerController(hal)
    reg = BoilerMap()
    slave = SimpleSlave(config.bus.addr_boiler, reg.read, reg.write)
    uart = None
    de = None
    if UART is not None:
        try:
            uart = UART(config.pins.rs485_uart_id, baudrate=config.bus.baudrate, tx=config.pins.rs485_tx, rx=config.pins.rs485_rx, timeout=0)
            de = Pin(config.pins.rs485_de, Pin.OUT, value=0)
        except Exception:
            uart = None
    while True:
        now = time.time()
        p = hal.pressure_bar()
        # Autofill coordination is decentralized; if a shared signal exists, read it here.
        state, reason = ctrl.tick(now_s=now, p_bar=p, autofill_active=False)
        # Publish status
        status_code = {"idle": 0, "heat": 1, "hold": 1, "inhibit": 2, "fault": 3}.get(state, 0)
        reason_code = {None: 0, "autofill": 1, "sensor_out_of_range": 2, "heater_on_timeout": 3, "watchdog_expired": 4}.get(reason, 0)
        reg.reg[0] = status_code
        reg.reg[1] = reason_code

        if uart is not None:
            data = uart.read()
            if data:
                resp = slave.feed_uart(data)
                if resp:
                    if de is not None:
                        de.value(1)
                    uart.write(resp)
                    uart.flush()
                    if de is not None:
                        de.value(0)
        hal.sleep_ms(200)


if __name__ == "__main__":
    main()
