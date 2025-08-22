# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-08-22

### Added

- RS485 Modbus RTU integration across core nodes:
	- Minimal RTU stack (`firmware/core/modbus_rtu.py`) with CRC16, ADU builder/checker, and `SimpleSlave` (0x03/0x06/0x10)
	- Per-node register maps (`firmware/core/modbus_maps.py`): status, reason, and tank_ok
	- Node boot loops serve Modbus: `boot_pump.py`, `boot_autofill.py`, `boot_boiler.py` (with DE pin handling)
- Desktop master helpers and CLIs:
	- `firmware/master/modbus_master.py` read-holding builder/parser
	- `firmware/master/aggregator_modbus_cli.py` JSON snapshot over serial
	- `tools/modbus_probe.py` single-read probe for bring-up
- Tank autonomy refactor:
	- `TankMonitor` core module and `tank_ok` interlocks in pump/autofill controllers
	- New tests for hysteresis and unknown behavior
- VS Code tasks:
	- “Modbus snapshot (aggregator CLI)” and “Modbus probe (single read)” with serial port/address prompts

### Changed

- Fixed Modbus CRC endianness and ADU wire-order handling; updated tests
- Docs:
	- Developer Guide: Modbus register map, addresses, and status/reason codes
	- Hardware: RS485 wiring matrix, topology ASCII diagram, troubleshooting, and quick checks
	- Bring-up: RS485 bus bring-up flow and probe task reference

### Dependencies

- Added optional `pyserial==3.5` for Modbus CLIs (requirements.txt)

## [0.1.1] - 2025-08-22

- Master: add Half Decent Scale BLE decoder and tare command; unit tests.
- Docs: mention BooKoo and Half Decent BLE support in Master UX.

## [0.1.0] - 2025-08-22

- Initial scaffold with safety primitives, boiler/autofill/pump controllers, HALs, tank sensor + service, Bookoo scale helpers, tests, and docs suite.
