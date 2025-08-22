# Architecture Overview

- Decentralized autonomous nodes using ESP32-WROOM-32E:
  - Boiler node: heater control via thermistor-derived steam pressure, interlocked with autofill.
  - Autofill node: boiler level probe and solenoid control; rate limits and timeout latch.
  - Pump/brew node: brew switch input, pump actuation with run-time/min-rest limits and starts-per-minute limiting.
- Optional Master (ESP32-S3): orchestration and UX; never compromises core safety.
- Language: MicroPython on device. Control logic is CPython-testable.

## Master Node Services (non-safety-critical)

- Tank Service (`firmware/master/tank_service.py`)
  - UART driver for DYP-A02YYUW ultrasonic sensor (`firmware/core/tank_sensor.py`).
  - Hysteresis-based alerts (ok/low/critical).
  - Line-based RPC: `get_level` -> `{ level_pct, state }`.

- Scale Service (`firmware/master/scale_service.py`)
  - Unified BLE protocol adapter for BooKoo and Half Decent (`firmware/master/scale_adapter.py`).
  - Decoders: `scale_bookoo.py` and `scale_halfdecent.py` (UUIDs, frames, commands).
  - Exponential smoothing, stability debounce, and derived flow (g/s).
  - Line-based RPC: `get_weight` -> `{ weight_g, flow_gps, stable, source }`, `tare` -> hex command.

- Aggregator (`firmware/master/aggregator_service.py`, `aggregator_rpc.py`)
  - Composes tank + scale into one dashboard payload: `{ tank:{...}, scale:{...} }`.
  - RPC: `get_status` for a single-shot combined view.

Notes:

- Master logic is advisory and never gates safety. Core nodes must reach safe states independently.
- BLE client scaffolding is optional; a fake notifier/runner is provided for local development.

## Module Boundaries

- Core nodes must be safe standalone: safe-off on fault, watchdog, plausibility checks.
- Inter-node signaling is advisory (e.g., autofill active) and must never be a single point of failure.

## Data Flow

- Inputs: NTC thermistor (boiler), level probe, brew switch; optional pressure transducer; ultrasonic tank level (DYP-A02YYUW) on master.
- Outputs: heater SSR/relay, pump, fill solenoid; optional indicators.

- Master inputs: BLE notifications from supported scales; UART frames from tank sensor.
- Master outputs: UX state/JSON over serial or network; BLE write commands (e.g., tare) via adapters.

## HAL Strategy

- `hal_mpy.py` provides GPIO/ADC access for MicroPython and degrades gracefully under CPython for tests.
- A minimal stub HAL exists for tests without MicroPython.

## Control Laws

- Boiler: hysteresis on estimated steam pressure; configurable via `BoilerConfig`.
- Autofill: edge-triggered fill with timeout and min-interval rate limiting.
- Pump: command-following with safety: max run time, min rest, starts-per-minute limit.

## Future Extensions

- PID or adaptive control (only if it adds value without compromising safety).
- Profiled brewing (requires additional sensors/UX; lives on master node).
- Extended UX: graphical dashboards, calibration tooling, and persisted logs.

