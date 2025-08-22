"""Modbus-based aggregator CLI (desktop).

Usage (example):
  python -m firmware.master.aggregator_modbus_cli --port /dev/ttyUSB0 --baud 9600

Requires pyserial if you want to actually talk to hardware. For tests, this module is importable without serial.
"""

import argparse
import json
import sys

try:
    import serial  # type: ignore
except Exception:  # pragma: no cover
    serial = None

from firmware.master.modbus_master import build_read_holding, parse_read_holding_response
from firmware.common import config


def poll_once(ser, addr: int, start: int, count: int):
    req = build_read_holding(addr, start, count)
    ser.write(req)
    ser.flush()
    ser.timeout = 0.2
    resp = ser.read(256)
    if not resp:
        return None
    _, vals = parse_read_holding_response(resp)
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=config.bus.baudrate)
    ns = ap.parse_args()
    if serial is None:
        print("pyserial not installed", file=sys.stderr)
        sys.exit(2)
    ser = serial.Serial(ns.port, baudrate=ns.baud, timeout=0.2)
    # Basic snapshot
    pump = poll_once(ser, config.bus.addr_pump, 0, 4) or (0, 0, 0)
    af = poll_once(ser, config.bus.addr_autofill, 0, 4) or (0, 0, 0)
    bo = poll_once(ser, config.bus.addr_boiler, 0, 4) or (0, 0)
    out = {
        "pump": {"status": pump[0], "reason": pump[1], "tank_ok": pump[2]},
        "autofill": {"status": af[0], "reason": af[1], "tank_ok": af[2]},
        "boiler": {"status": bo[0], "reason": bo[1]},
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
