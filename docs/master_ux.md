# Master UX

The master node (ESP32-S3) provides user-facing information and controls, without impacting core safety.

## Tank Level

- Reads DYP-A02YYUW ultrasonic sensor via UART (9600-8N1).
- Displays percent fill and a simple bar/graph.
- Alerts:
  - Low: below `tank.low_pct` (with `hysteresis_pct`).
  - Critical: below `tank.critical_pct`.

## Prompts and Actions

- Low tank: show a non-blocking warning; suggest refill soon.
- Critical tank: prominent warning; optionally inhibit non-critical operations in the master UX only.
- Prime pump (maintenance): guided steps to prime the line after service; never bypasses core node safeties.

## Integration

- RPC: master exposes `get_level` returning JSON `{ level_pct, state }` (see `firmware/master/tank_service.py`).
- RPC (scales): master provides `get_weight` returning `{ weight_g, flow_gps, stable, source }` and `tare` command that returns bytes as hex (see `firmware/master/scale_service.py`).
- RPC (aggregate): optional endpoint can return both tank and scale data: `{ tank:{level_pct,state}, scale:{weight_g,flow_gps,stable,source} }` (see `firmware/master/aggregator_service.py`).
- BLE Scales:
  - BooKoo Themis/Mini: Service 0x0FFE, Data 0xFF11, Command 0xFF12. See `firmware/master/scale_bookoo.py`.
  - Half Decent: Service `0000fff0-0000-1000-8000-00805f9b34fb`, Notify `0000fff4-0000-1000-8000-00805f9b34fb`, Write `000036f5-0000-1000-8000-00805f9b34fb`. See `firmware/master/scale_halfdecent.py`.
- Core nodes remain autonomous; UX is advisory.
