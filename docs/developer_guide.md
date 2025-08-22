# Developer Guide & Contribution

## Project Layout

- `firmware/common`: shared config and safety primitives
- `firmware/core`: autonomous node controllers and HALs
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

## Release & Deployment

- Tag changes and record in `CHANGELOG.md`.
- Deploy node-specific files to devices via `mpremote`/`rshell`.
