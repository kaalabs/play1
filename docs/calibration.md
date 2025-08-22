# Calibration Guide

This guide helps you calibrate sensor readings to the Domobar Classic/Standard.

## Thermistor (temperature -> pressure)

- Ensure good thermal coupling and insulation of the NTC to the boiler shell.
- With machine at steady state, record:
  - NTC ADC counts and computed temperature
  - Observed steam pressure (external gauge or relief onset)
- Adjust the temperature-to-pressure mapping if systematic bias is observed.
  - Option A: tweak Antoine coefficients in `HAL.steam_pressure_from_temp_c`.
  - Option B: implement a simple 2–3 point linearization table.

## Pressure Transducer (optional)

- Record ADC counts at known pressures (0 bar, ~1 bar, ~2 bar) using a reference gauge.
- Fit a line and update the mapping in `HAL.read_pressure_bar` (v_min/v_max/bar_max and divider).

## Linearization helper

You can apply a simple piecewise-linear mapping using `firmware/common/utils.py`:

- Collect 2–3 calibration points (e.g., temperature -> pressure or ADC -> bar).
- Build a `Linearizer([(x0, y0), (x1, y1), (x2, y2)])` and use it to map raw to engineering units.
- For MicroPython deployment, precompute points and embed them in config.
