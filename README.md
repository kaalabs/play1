# Domobar Control System (MicroPython)

Decentralized, safety-first control system for the Vibiemme Domobar Standard Inox (aka new Domobar RVS), built on ESP32 MCUs with MicroPython.

Priorities (descending): safety, robustness, maintainability, modularity, ease-of-use, innovative features, non-invasive UX.

## Architecture

- Core nodes (ESP32-WROOM-32E), fully autonomous and responsible for their own safety:
  - Boiler control (heater, steam/boiler pressure control, autofill interlocks)
  - Pump/brew control (brew switch input, pump actuation, optional profiling)
  - Autofill control (level probe, fill valve + pump coordination)
- Optional Master (ESP32-S3): orchestration and UX only; never compromises core safety.
- Language: MicroPython 1.21+ (portable logic validated under CPython for unit tests).

## Safety Concept

- Hardware-first: retain factory primary safety devices (pressurestat/thermostats, thermal fuse, relief valve) in series. SSRs only reduce duty, never bypass primary safety.
- Software safety: each core node has watchdog, fault latching, timeouts, sensor plausibility checks, and safe-state fallback.
- Non-invasive: default behavior mirrors stock machine; advanced features only when explicitly enabled.
- Default sensing: boiler thermistor -> saturation pressure mapping (non-invasive). A pressure transducer is optional. See SPECS.md.

## Repo Layout

- `firmware/common/` shared HAL, safety, config, utilities
- `firmware/core/` autonomous core control modules and entrypoint
- `firmware/master/` (placeholder) UX/orchestration
- `tests/` CPython unit tests for control logic
- `docs/` full documentation set (architecture, safety, hardware, bring-up, maintenance, troubleshooting, developer guide)

## Getting Started

1. Install Python 3.11+ for local tests
2. Install dev dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

1. Flash MicroPython to ESP32s and deploy `firmware/core` files with your preferred tool (mpremote/rshell/Thonny). Configure pins in `firmware/common/config.py`.

## Configuration

See `firmware/common/config.py` for machine parameters (boiler target pressure, hysteresis, timeouts) and GPIO mapping. Adjust to your specific Domobar variant and mains (e.g., 230V/50Hz).

## Status

- Boiler controller: hysteresis control with safety interlocks (thermistor-based pressure estimation), unit-tested
- Autofill controller: debounce, timeout, interlocks; unit-tested
- Pump controller: rate limiting and max-run safety; unit-tested
- HAL (MicroPython + CPython stub): GPIO/ADC/UART, status LED, logging
- Master integrations:
  - Tank sensor (DYP-A02YYUW) driver + service with alerts and simple JSON RPC
  - BLE scale helpers: BooKoo Themis/Mini and Half Decent decoders + basic commands

## Documentation

See the `docs/` folder:

- Architecture: `docs/architecture.md`
- Safety: `docs/safety.md`
- Hardware: `docs/hardware.md`
- Bring-up: `docs/bringup.md`
- Maintenance: `docs/maintenance.md`
- Troubleshooting: `docs/troubleshooting.md`
- Developer Guide: `docs/developer_guide.md`

Docs site (MkDocs Material): configured in `mkdocs.yml`. To serve locally:

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

## License

MIT
