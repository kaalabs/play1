# Maintenance & Service Procedures

Audience: trained maintenance engineers.

## Safety

- Disconnect mains. Verify absence of voltage.
- Allow boiler to cool and depressurize before opening.

## Periodic Checks

- Visual inspection of wiring, connectors, and chassis ground.
- Verify operation of factory safeties (thermostats, relief valve) per OEM guidance.
- Check SSR/relay modules for heat and proper mounting.

## Service Actions

- Replacing thermistor: remove insulating wrap, clean contact, apply fresh thermal paste, rewrap.
- Replacing SSR/relay: match voltage/current rating; test with isolation.
- Updating firmware: redeploy `firmware/common` and node `firmware/core` files; verify setpoints.

## Diagnostics

- Fault latch reasons reported over UART/log (planned: LEDs or display on master).
- Use multimeter to verify probe, SSR outputs, and supply rails.
