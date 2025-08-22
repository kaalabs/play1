# Vibiemme Domobar Classic / Standard (RVS) – Working Specs and Notes

This document collects verified specs and assumptions for parameterization. Replace TBDs with measured values.

## Machine Topology (confirmed vs assumptions)

- Single copper boiler, 0.6 L (confirmed: source below)
- E61 brew group (confirmed)
- Reservoir-fed, vibration pump (confirmed)
- Adjustable thermostat in stock control (confirmed); no stock PID
- Pump pressure gauge (confirmed); no explicit boiler pressure gauge on this variant
- Safety devices (typical/assumed): thermal cutoff, boiler safety valve; keep stock devices in series

## Electrical

- Mains: 230V/50Hz (Netherlands/EU default) or 120V/60Hz (US). Configure in `config.system.mains`.
- Heater: 1.4 kW (confirmed); use SSR/relay with proper isolation; never bypass stock thermal protections.

## Sensors/Actuators Mapping

- Boiler sensing options:
	- Preferred (non-invasive): boiler temperature sensor (NTC/thermistor) bonded to boiler shell; map to steam pressure via saturation curve.
	- Alternative (more invasive): add 0.5–4.5V boiler pressure transducer on a spare port, scaled via divider to ESP32 ADC.
- Autofill level: stock probe via conditioner (digital) or ADC threshold if analog.
- Actuators: heater SSR/relay, fill solenoid, pump; driven via opto-isolated drivers.

## Control Parameters (initial)

- Boiler steam target: ~1.1 bar equivalent; hysteresis 0.15 bar (or equivalent temperature band when temp-controlled).
- Autofill timeout: 30 s; min interval 20 s.
- Pump run max: 120 s; min rest 5 s.

## Compliance & Safety

- Respect IEC 60335-1/-2-15 concepts for household appliances (creepage, protective earth, insulation, temperature limits).
- Maintain hardware primary safety chain; software adds secondary protections only.

## Open Questions

- Exact Domobar Standard Inox generation and wiring.
- Native control board behavior to mirror for non-invasive mode.
- Sensor models and calibration constants.

## References

- Product page (Dutch): VBM Domobar Classic/Standard — Eembergen. Key specs: copper boiler 0.6 L, E61 group, vibration pump, pump manometer, adjustable thermostat, 1.4 kW heating, stainless steel housing. <https://eembergen.nl/product/vbm-domobar-classic/>
