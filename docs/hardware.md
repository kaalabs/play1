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

## RS485 (Modbus RTU) Wiring

- Use a differential RS485 transceiver (e.g., MAX485, SN75176) on each node.
- Bus topology: multi-drop A/B twisted pair; daisy-chain preferred; avoid stubs.
- Termination: 120 Ω across A/B at the two physical ends of the bus only.
- Biasing: one location should provide fail-safe bias (e.g., 680 Ω–1 kΩ pull-up on A, pull-down on B) so the bus idles HIGH/mark.
- DE/RE handling: tie RE low (enable receiver) and drive DE high only during TX. Our firmware toggles a dedicated `rs485_de` GPIO around UART writes.
- UART: 9600 8N1 by default; ensure all nodes share baud rate. Wire UART TX/RX to DI/RO on the transceiver.
- Shielding: use shielded twisted pair if noise is present; connect shield to earth at one point only.

### Wiring matrix (typical transceiver)

| Function | RS485 transceiver pin | Connects to | Notes |
|---|---|---|---|
| UART TX | DI | MCU UART TX (see `Pins.rs485_tx`) | MCU drives DI; goes out on bus |
| UART RX | RO | MCU UART RX (see `Pins.rs485_rx`) | Transceiver drives RO to MCU |
| Driver enable | DE | MCU GPIO (see `Pins.rs485_de`) | High during TX only |
| Receiver enable | RE | Tie to DE or GND (active low) | Tie to DE for auto half-duplex, or GND to always listen |
| Bus A | A (a.k.a. D+) | RS485 bus A | Keep A-to-A across all nodes |
| Bus B | B (a.k.a. D−) | RS485 bus B | Keep B-to-B across all nodes |
| Power | VCC | 3.3 V or 5 V per transceiver | Ensure logic-level compatibility with MCU |
| Ground | GND | Common ground | Required reference between nodes |

Notes:

- Some boards label A/B inverted (D+/D−). If the bus idles low or you see framing errors, swap A/B on that device.
- Many MAX485 modules are 5 V. They typically accept 3.3 V logic on DI ( VIH ≈ 2.0 V ), but verify your module; choose a 3.3 V variant or add level shifting if needed.
- USB–RS485 adapters connect directly to the A/B pair; do not cross A↔B.

### Bus topology (ASCII)

```text
[PC USB‑RS485]--A/B--[Node 1]--A/B--[Node 2]--A/B--[Node 3]
	|                                        |
     120Ω                                     120Ω
 (terminator)                             (terminator)
```

- Only the two physical ends of the bus are terminated (120 Ω across A/B).
- Keep A-to-A and B-to-B throughout the chain; avoid long stubs.
- Provide fail-safe bias at one location so the line idles mark when idle.

### Troubleshooting

- Continuous framing errors or no responses
	- Likely cause: A/B swapped on one device
	- Fix: Swap A and B on that device; keep A-to-A and B-to-B across the bus

- Works only when touching wires or only some nodes respond
	- Likely cause: Missing termination or fail-safe bias
	- Fix: Add 120 Ω terminators at both physical ends; add a single bias point (pull-up on A, pull-down on B)

- Collisions or garbled replies with multiple nodes
	- Likely cause: DE stuck high (driver always enabled) or more than one master
	- Fix: Ensure firmware drives `rs485_de` high only while transmitting; ensure only one bus master

- Intermittent timeouts on longer runs
	- Likely cause: Long stubs or noise coupling
	- Fix: Shorten stubs, use twisted pair, add shielding, and ground shield at one end only

- Nodes reset when bus transmits
	- Likely cause: Power/level issues (5 V transceiver with 3.3 V MCU) or poor decoupling/grounding
	- Fix: Use 3.3 V-compatible transceivers or proper level shifting; add decoupling caps and ensure solid ground reference

- No data or gibberish at expected wiring
	- Likely cause: Baud/parity mismatch
	- Fix: Set all devices to `9600 8N1` (default) or update `BusConfig.baudrate` consistently

### Quick checks (meter/scope)

- Continuity
	- Verify A-to-A and B-to-B continuity across all nodes; no A↔B cross anywhere
	- Shield (if used) has continuity end-to-end but is grounded at one end only

- Termination
	- Measure resistance between A and B with power off: ≈120 Ω at an end with one terminator; ≈60 Ω across the full bus with two terminators

- Fail-safe bias (power on, idle)
	- With bias present, A should be higher than B by roughly 0.2–1.5 V when idle (RO idles high/mark)
	- Without bias, A–B hovers near 0 V and the receiver may chatter

- DE/RE and RO behavior
	- `rs485_de` pin idles low; pulses high only during transmit frames
	- MCU UART RX (RO) idles high (mark) and shows clean 9600 8N1 frames during traffic

- Baud and framing
	- Confirm all devices use the same settings (default `9600 8N1`); a logic analyzer helps verify byte timing and CRC ordering

## Pin Mapping Template

Update `firmware/common/config.py`:

- heater_ssr: GPIOxx
- autofill_valve: GPIOxx
- pump: GPIOxx
- autofill_probe: GPIOxx (or ADC)
- boiler_temp_ain: ADC1_CHx
- tank_uart_id/tx/rx: UART id and pins for DYP-A02YYUW (master node)

