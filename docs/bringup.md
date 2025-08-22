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

## Calibration (optional)

- Compare estimated pressure (from temp) against an external gauge or relief-valve lift.
- If using a pressure transducer, record raw ADC and actual pressure points and update the mapping in HAL.
