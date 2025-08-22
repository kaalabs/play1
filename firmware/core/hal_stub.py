# Minimal HAL abstraction used by controllers; provide MicroPython and CPython stubs

class HAL:
    def __init__(self, heater_cb=None, pump_cb=None):
        self._heater_cb = heater_cb
        self._pump_cb = pump_cb
        self.heater_state = False
        self.pump_state = False

    def heater(self, on: bool):
        self.heater_state = bool(on)
        if self._heater_cb:
            self._heater_cb(self.heater_state)

    def pump(self, on: bool):
        self.pump_state = bool(on)
        if self._pump_cb:
            self._pump_cb(self.pump_state)
