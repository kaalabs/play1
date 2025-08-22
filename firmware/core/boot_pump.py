"""MicroPython entrypoint for Pump/Brew Node."""

import time
from firmware.core.hal_mpy import HAL
from firmware.core.pump_controller import PumpController
from firmware.core.tank_monitor import TankMonitor
from firmware.core.modbus_rtu import SimpleSlave
from firmware.core.modbus_maps import PumpMap
from firmware.common import config

try:
    from machine import UART, Pin
except Exception:  # pragma: no cover
    UART = None
    Pin = None


def main():
    hal = HAL()
    tank = TankMonitor()
    ctrl = PumpController(hal)
    reg = PumpMap()
    slave = SimpleSlave(config.bus.addr_pump, reg.read, reg.write)

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
        brew = hal.brew_switch()
        state, reason = ctrl.tick(now_s=now, brew_switch=brew, tank_ok=tank.tank_ok)
        # Publish registers
        status_code = {"idle": 0, "run": 1, "inhibit": 2, "fault": 3}.get(state, 0)
        reason_code = {
            None: 0,
            "rest": 1,
            "rate_limit": 2,
            "tank_not_ok": 3,
            "watchdog_expired": 4,
            "pump_run_timeout": 5,
        }.get(reason, 0)
        reg.reg[0] = status_code
        reg.reg[1] = reason_code
        reg.reg[2] = 1 if tank.tank_ok else 0

        # Handle Modbus if UART available
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
        hal.sleep_ms(50)


if __name__ == "__main__":
    main()
