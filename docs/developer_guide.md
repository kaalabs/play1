# Developer Guide & Contribution

## Project Layout

- `firmware/common`: shared config and safety primitives
- `firmware/core`: autonomous node controllers and HALs
- `firmware/core/tank_monitor.py`: local tank level state machine (ok/low/critical/unknown)
- `tests`: CPython unit tests for core logic
- `docs`: documentation set

## Local Dev

- Python 3.11+ recommended for tests
- Create venv, `pip install -r requirements.txt`, run `pytest -q`

### Master-side helpers

- Scale smoke test: use VS Code task "Scale smoke (fake BLE)" to stream demo frames into the scale service and print JSON.
- Aggregator RPC: use the "Aggregator RPC (stdin/stdout)" task, and send `get_status` on stdin to receive combined tank + scale status.
- Real BLE (desktop): optional bleak scaffold exists in `firmware/master/ble_client.py` (not a hard dependency). Wire your notify callback to `ScaleService.on_notify()`.
- BLE Bridge (desktop): `firmware/master/ble_bridge.py` provides a ready-to-run bleak bridge. Try the VS Code task "BLE Bridge (desktop, bleak)" or run it manually with `--source bookoo|halfdecent` and either `--address` or `--name`.

### Logging

- Convert readings to CSV: pipe JSON lines into `tools/scale_logger.py -o out.csv`.
- VS Code task: "Scale -> CSV (fake stream)" pipes the demo runner into the CSV logger and writes `/tmp/scale.csv`.
- VS Code task: "BLE Live -> CSV (bridge)" pipes the bleak-based bridge into the CSV logger to capture real sessions at `/tmp/scale_live.csv`.

## Coding Standards

- Favor pure-Python logic for testability; isolate MicroPython APIs in HAL.
- Keep core safety behaviors covered by tests.
- Update docs with any behavior or interface change.

## Adding a Feature

1. Propose design if it touches core behaviors/safety.
2. Add or update tests (happy path + edge/fault cases).
3. Implement feature with minimal HAL surface.
4. Update docs: architecture, safety (if relevant), bring-up, troubleshooting.
5. Update `CHANGELOG.md`.

## Tank autonomy refactor

- The tank sensor is now owned by core via `TankMonitor`, which wraps `TankLevel` and applies hysteresis.
- Controllers accept a new `tank_ok` parameter:
	- `AutofillController.tick(..., tank_ok=True)` inhibits fill if false.
	- `PumpController.tick(..., tank_ok=True)` inhibits pump if false.
- Main loops updated:
	- `boot_autofill.py` samples `TankMonitor` each cycle and passes `tank_ok`.
	- `boot_pump.py` does the same for the pump node.
- The master `tank_service.py` remains for UX/telemetry but is no longer required for safety.

## Release & Deployment

- Tag changes and record in `CHANGELOG.md`.
- Deploy node-specific files to devices via `mpremote`/`rshell`.

### RS485 / Modbus helpers

- Snapshot registers from nodes over RS485: use the VS Code task "Modbus snapshot (aggregator CLI)" and provide your serial port (e.g., `/dev/tty.usbserial-1101`). It prints a one-line JSON of pump, autofill, and boiler status. Requires `pyserial` at runtime.

Register map (Holding Registers 0x03):

- 0x0000: status code
- 0x0001: reason code
- 0x0002: tank_ok (0/1; pump/autofill only)
- 0x0003: reserved

Node addresses (default): pump=1, autofill=2, boiler=3, master=10. See `firmware/common/config.py` BusConfig.

Status/Reason codes:

- Pump
	- status: 0=idle, 1=run, 2=inhibit, 3=fault
	- reason: 0=none, 1=rest, 2=rate_limit, 3=tank_not_ok, 4=watchdog_expired, 5=pump_run_timeout
- Autofill
	- status: 0=ok, 1=fill, 2=inhibit, 3=fault
	- reason: 0=none, 1=rate_limit, 2=tank_not_ok, 3=fill_timeout, 4=watchdog_expired
- Boiler
	- status: 0=idle, 1=heat/hold, 2=inhibit, 3=fault
	- reason: 0=none, 1=autofill, 2=sensor_out_of_range, 3=heater_on_timeout, 4=watchdog_expired
