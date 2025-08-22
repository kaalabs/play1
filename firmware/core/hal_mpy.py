"""MicroPython HAL for ESP32 nodes (boiler/autofill/pump)."""

try:
    from machine import Pin, ADC
    import time
    MICROPY = True
except ImportError:  # allow import under CPython for tooling
    MICROPY = False
    Pin = object  # type: ignore
    ADC = object  # type: ignore
    import time

from firmware.common import config


class HAL:
    def __init__(self, pins: config.Pins = config.pins):
        self.pins = pins
        # Outputs
        self._heater_pin = None
        self._fill_valve_pin = None
        self._pump_pin = None
        # Inputs
        self._pressure_adc = None
        self._temp_adc = None
        self._probe_pin = None
        self._brew_switch_pin = None
        # LED
        self._led_pin = None

        if MICROPY:
            if getattr(pins, "heater_ssr", None) is not None:
                self._heater_pin = Pin(pins.heater_ssr, Pin.OUT, value=0)
            if getattr(pins, "autofill_valve", None) is not None:
                self._fill_valve_pin = Pin(pins.autofill_valve, Pin.OUT, value=0)
            if getattr(pins, "pump", None) is not None:
                self._pump_pin = Pin(pins.pump, Pin.OUT, value=0)
            if getattr(pins, "boiler_pressure_ain", None) is not None:
                self._pressure_adc = ADC(Pin(pins.boiler_pressure_ain))
                try:
                    self._pressure_adc.atten(ADC.ATTN_11DB)
                    self._pressure_adc.width(ADC.WIDTH_12BIT)
                except Exception:
                    pass
            if getattr(pins, "boiler_temp_ain", None) is not None:
                self._temp_adc = ADC(Pin(pins.boiler_temp_ain))
                try:
                    self._temp_adc.atten(ADC.ATTN_11DB)
                    self._temp_adc.width(ADC.WIDTH_12BIT)
                except Exception:
                    pass
            if getattr(pins, "autofill_probe", None) is not None:
                self._probe_pin = Pin(pins.autofill_probe, Pin.IN)
            if getattr(pins, "brew_switch", None) is not None:
                try:
                    self._brew_switch_pin = Pin(pins.brew_switch, Pin.IN, Pin.PULL_UP)
                except Exception:
                    self._brew_switch_pin = Pin(pins.brew_switch, Pin.IN)
            if getattr(pins, "status_led", None) is not None:
                self._led_pin = Pin(pins.status_led, Pin.OUT, value=0)

        # Software mirror for CPython and for state reporting
        self.heater_state = False
        self.fill_valve_state = False
        self.pump_state = False

    # Actuators
    def heater(self, on: bool):
        self.heater_state = bool(on)
        if MICROPY and self._heater_pin is not None:
            self._heater_pin.value(1 if on else 0)

    def fill_valve(self, on: bool):
        self.fill_valve_state = bool(on)
        if MICROPY and self._fill_valve_pin is not None:
            self._fill_valve_pin.value(1 if on else 0)

    def pump(self, on: bool):
        self.pump_state = bool(on)
        if MICROPY and self._pump_pin is not None:
            self._pump_pin.value(1 if on else 0)

    # Sensors
    def read_pressure_bar(self) -> float:
        """Linear mapping for a typical 0.5–4.5V ratiometric sensor to 0–3 bar. Calibrate on hardware."""
        if MICROPY and self._pressure_adc is not None:
            raw = self._pressure_adc.read()
            volts = (raw / 4095.0) * 3.6
        else:
            volts = 0.0
        v_min, v_max, bar_max = 0.5, 4.5, 3.0
        divider = 1.0
        v_eff = volts * divider
        if v_eff <= v_min:
            return 0.0
        if v_eff >= v_max:
            return bar_max
        return (v_eff - v_min) * (bar_max / (v_max - v_min))

    # Thermistor path
    def read_boiler_temp_c(self) -> float:
        if MICROPY and self._temp_adc is not None:
            counts = self._temp_adc.read()
        else:
            counts = config.thermistor.adc_fullscale_counts // 2
        cfg = config.thermistor
        v = (counts / cfg.adc_fullscale_counts) * cfg.vref_v
        if v <= 0.001 or v >= (cfg.vref_v - 0.001):
            return 25.0
        rt = cfg.pullup_ohm * (v / (cfg.vref_v - v))
        import math
        t0_k = (cfg.t0_c + 273.15)
        inv_t = (1.0 / t0_k) + (1.0 / cfg.beta) * math.log(rt / cfg.r0_ohm)
        t_k = 1.0 / inv_t
        return t_k - 273.15

    @staticmethod
    def steam_pressure_from_temp_c(temp_c: float) -> float:
        import math
        A, B, C = 8.14019, 1810.94, 244.485
        p_mmHg = 10 ** (A - (B / (C + temp_c)))
        p_bar_abs = p_mmHg / 750.062
        return max(0.0, p_bar_abs - 1.01325)

    def read_pressure_bar_via_temp(self) -> float:
        t = self.read_boiler_temp_c()
        return self.steam_pressure_from_temp_c(t)

    def pressure_bar(self) -> float:
        mode = getattr(config.boiler, "control_mode", "temp")
        return self.read_pressure_bar_via_temp() if mode == "temp" else self.read_pressure_bar()

    def probe_wet(self) -> bool:
        if MICROPY and self._probe_pin is not None:
            return bool(self._probe_pin.value())
        return False

    def brew_switch(self) -> bool:
        if MICROPY and self._brew_switch_pin is not None:
            # If pull-up used, switch pressed may be low; invert if needed during bring-up
            return not bool(self._brew_switch_pin.value())
        return False

    def sleep_ms(self, ms: int):
        time.sleep(ms / 1000.0)

    # Diagnostics
    def led(self, on: bool):
        if MICROPY and self._led_pin is not None:
            self._led_pin.value(1 if on else 0)

    def log(self, *args):
        try:
            print(*args)
        except Exception:
            pass
 
