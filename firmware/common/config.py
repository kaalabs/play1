# Machine configuration and GPIO mapping for Domobar Standard Inox
# Adjust per machine variant and mains

from typing import NamedTuple


class BoilerConfig(NamedTuple):
    target_bar: float = 1.1  # steam pressure target
    hysteresis_bar: float = 0.15
    max_continuous_on_s: int = 180  # SSR duty safety timeout
    min_off_recovery_s: int = 10
    sensor_min_bar: float = 0.2
    sensor_max_bar: float = 2.5
    control_mode: str = "temp"  # "pressure" or "temp"


class ThermistorConfig(NamedTuple):
    # Beta model parameters; adjust to your sensor (e.g., 100k NTC, Beta 3950)
    r0_ohm: float = 100_000.0
    t0_c: float = 25.0
    beta: float = 3950.0
    pullup_ohm: float = 100_000.0
    # ADC and voltage assumptions for conversion
    vref_v: float = 3.3
    adc_fullscale_counts: int = 4095


class AutofillConfig(NamedTuple):
    fill_timeout_s: int = 30
    min_refill_interval_s: int = 20
    debounce_ms: int = 30


class PumpConfig(NamedTuple):
    max_run_s: int = 120
    min_rest_s: int = 5
    max_starts_per_min: int = 6
    debounce_ms: int = 30


class TankLevelConfig(NamedTuple):
    # Distances measured by ultrasonic sensor (sensor mounted on tank lid, facing water)
    full_distance_mm: int = 40    # distance from sensor to water at FULL
    empty_distance_mm: int = 200  # distance from sensor to water at EMPTY
    smoothing_alpha: float = 0.3  # optional EMA smoothing factor for UI
    sample_hz: int = 10           # sensor nominal output rate
    low_pct: float = 20.0         # alert threshold for low tank
    critical_pct: float = 5.0     # alert threshold for critically low tank
    hysteresis_pct: float = 2.0   # hysteresis to avoid alert flapping


class BusConfig(NamedTuple):
    # Modbus/RS485 bus configuration and addresses
    baudrate: int = 9600
    addr_pump: int = 1
    addr_autofill: int = 2
    addr_boiler: int = 3
    addr_master: int = 10


class Pins(NamedTuple):
    # Assign actual GPIOs during bring-up
    heater_ssr: int = 25
    boiler_pressure_ain: int = 36  # ADC1_CH0
    boiler_temp_ain: int = 39       # ADC1_CH3 (example for thermistor divider)
    autofill_probe: int = 34       # ADC1_CH6 or digital input via conditioner
    autofill_valve: int = 26
    pump: int = 27
    brew_switch: int = 14
    watchdog_kick: int = 33  # optional external watchdog
    status_led: int = 2      # optional status LED
    # Master node: tank level UART (DYP-A02YYUW)
    tank_uart_id: int = 1
    tank_uart_tx: int = 17
    tank_uart_rx: int = 16
    # RS485 UART and Driver Enable pin (DE/RE tied)
    rs485_uart_id: int = 2
    rs485_tx: int = 15
    rs485_rx: int = 4
    rs485_de: int = 5


class System(NamedTuple):
    mains: str = "230V_50Hz"
    model: str = "Vibiemme Domobar Standard Inox"


boiler = BoilerConfig()
thermistor = ThermistorConfig()
autofill = AutofillConfig()
pump = PumpConfig()
tank = TankLevelConfig()
bus = BusConfig()
pins = Pins()
system = System()
