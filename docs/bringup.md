# First Bring-up and Calibration

Prereqs:

- MicroPython flashed on ESP32 nodes
- Verified wiring per hardware guide
- Python env ready for tests

## Steps

1. Configure pins and thermistor parameters in `firmware/common/config.py`.
2. Unit-test locally: `pytest -q`.
3. Deploy to boiler node: copy `firmware/common` and `firmware/core` (including `boot_boiler.py`) to the ESP32.
4. Power on with heater physically disconnected for the first run. Observe temp reading via UART/debug prints if added.
5. Verify thermistor reading rises with gentle heat. Adjust `ThermistorConfig` if needed.
6. Connect heater through SSR and perform low-duty test: set target to low pressure/temp, confirm hysteresis behavior and safe-off on faults.
7. Pump node: verify pump toggles with brew switch input. Confirm min rest inhibit and that run-time timeout trips a fault as expected.

## RS485 Bus Bring-up

1. Wire RS485 A/B daisy-chain with 120 Ω terminators at both ends and a single bias point.
2. Configure `Pins.rs485_*` and `BusConfig` in `firmware/common/config.py` (baud/address).
3. Power nodes and connect your USB-RS485 adapter to the PC. Note the serial port path (e.g., `/dev/tty.usbserial-1101`).
4. In VS Code, run the task "Modbus snapshot (aggregator CLI)" and enter the serial port. You should see JSON with status/reason codes.
5. Sanity checks:
	- Disconnect one node: its section should time out or show zeros; reconnect and verify it reappears.
	- Toggle brew switch or lift the boiler level probe and observe status/reason changes.
	- If no responses, verify DE polarity and that only the master is driving the bus when transmitting.
6. Optional: run "Modbus probe (single read)" to query a specific node/address and registers for quick checks during wiring.

## Calibration (optional)

- Compare estimated pressure (from temp) against an external gauge or relief-valve lift.
- If using a pressure transducer, record raw ADC and actual pressure points and update the mapping in HAL.
