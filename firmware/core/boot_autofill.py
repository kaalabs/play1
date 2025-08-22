"""MicroPython entrypoint for Autofill Node."""

from firmware.core.hal_mpy import HAL
from firmware.core.autofill_controller import AutofillController
from firmware.core.tank_monitor import TankMonitor
from firmware.core.modbus_rtu import SimpleSlave
from firmware.core.modbus_maps import AutofillMap
from firmware.common import config
try:
    from machine import UART, Pin
except Exception:  # pragma: no cover
    UART = None
    Pin = None
import time


def main():
    hal = HAL()
    tank = TankMonitor()
    ctrl = AutofillController(hal)
    reg = AutofillMap()
    slave = SimpleSlave(config.bus.addr_autofill, reg.read, reg.write)
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
        tank.sample()
        wet = hal.probe_wet()
        state, reason = ctrl.tick(now_s=now, probe_wet=wet, tank_ok=tank.tank_ok)
        # Publish
        status_code = {"ok": 0, "fill": 1, "inhibit": 2, "fault": 3}.get(state, 0)
        reason_code = {
            None: 0,
            "rate_limit": 1,
            "tank_not_ok": 2,
            "fill_timeout": 3,
            "watchdog_expired": 4,
        }.get(reason, 0)
        reg.reg[0] = status_code
        reg.reg[1] = reason_code
        reg.reg[2] = 1 if tank.tank_ok else 0

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
        hal.sleep_ms(100)


if __name__ == "__main__":
    main()
