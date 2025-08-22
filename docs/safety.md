# Safety Case and Requirements

Principles:

1. Hardware-first safety: retain factory safety chain (thermostats/thermal fuses/relief valves/pressurestat where applicable).
2. Software adds secondary protections: watchdogs, latching faults, plausibility checks, timeouts, safe-off defaults.
3. Decentralization: each core node must be safe if isolated from others.
4. Non-invasive default: stock behavior unless advanced features are explicitly enabled.

## Safety Functions

- Boiler overheat/overpressure prevention via conservative setpoints and hysteresis.
- Heater inhibition during autofill.
- Fill timeout and min interval.
- Pump run-time limit and min rest (planned).

## Fault Handling

- Latching faults stop actuators until service action clears them.
- Fault reasons are retained and exposed via diagnostics.

## Standards and Practices

- Design aligns with IEC 60335-1/-2-15 concepts (household appliance safety).
- Electrical design to respect insulation, PE continuity, creepage/clearance, and EMC best practices.
- SSR/relay drivers shall provide isolation and snubbing as required by the load.

