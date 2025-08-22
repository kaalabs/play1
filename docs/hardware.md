# Hardware Wiring and Components

Warning: Mains voltage is lethal. Only qualified personnel should service or modify wiring. Always disconnect power and verify.

## MCU Selection

- ESP32-WROOM-32E for core nodes, ESP32-S3 for master UX.

## Sensors

- Boiler thermistor: 100k NTC (Beta ~3950) bonded to boiler shell; divider with 100k pull-up to 3.3V.
- Level probe: digital via conditioner (optocoupler/AC sensing) preferred.
- Optional pressure transducer: 0.5–4.5V ratiometric with divider and filtering.
- Tank level (DYP-A02YYUW ultrasonic, on master): 5V supply, TTL UART 9600-8N1. Mount on tank lid facing water; ensure clear path and avoid splashes/condensation. Use level shifting or 5V-tolerant UART as needed.

## Actuators

- Heater SSR/relay rated for 1.4 kW at mains; zero-cross SSR preferred.
- Fill solenoid driver: opto-isolated triac or relay module.
- Pump driver: relay/SSR with surge handling.

## Grounding and Isolation

- Maintain protective earth to chassis and group head.
- Ensure control ground is isolated from mains where necessary; use proper opto/isolation barriers.

## Pin Mapping Template

Update `firmware/common/config.py`:

- heater_ssr: GPIOxx
- autofill_valve: GPIOxx
- pump: GPIOxx
- autofill_probe: GPIOxx (or ADC)
- boiler_temp_ain: ADC1_CHx
- tank_uart_id/tx/rx: UART id and pins for DYP-A02YYUW (master node)

