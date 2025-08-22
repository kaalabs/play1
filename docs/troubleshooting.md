# Troubleshooting

Symptom -> Checks:

- No heat: verify mains, SSR control pin, thermistor reading plausibility, latch status, factory thermostats.
- Rapid cycling: increase hysteresis or check thermistor bonding; verify SSR not sticking.
- Autofill never stops: probe signal stuck dry; check conditioner; see fill timeout fault.
- Frequent autofills: check reservoir level and probe conductivity; adjust min interval.
- Pump won’t run: check brew switch debounce and pump driver; confirm run-time limit not tripping.

Logs/Indicators:

- Planned: UART status lines from nodes; LED heartbeat patterns.
