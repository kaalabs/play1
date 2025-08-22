"""Quick Modbus probe tool.

Sends a single Read Holding Registers to a node and prints the values.

Usage examples:
  python tools/modbus_probe.py --port /dev/tty.usbserial-1101 --addr 1 --start 0 --count 4
"""

import argparse
import sys

try:
    import serial  # type: ignore
except Exception:  # pragma: no cover
    serial = None

from firmware.master.modbus_master import build_read_holding, parse_read_holding_response


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--addr", type=int, required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--timeout", type=float, default=0.4)
    ns = ap.parse_args()
    if serial is None:
        print("pyserial not installed", file=sys.stderr)
        sys.exit(2)
    ser = serial.Serial(ns.port, baudrate=ns.baud, timeout=ns.timeout)
    req = build_read_holding(ns.addr, ns.start, ns.count)
    ser.write(req)
    ser.flush()
    resp = ser.read(256)
    if not resp:
        print("no response")
        sys.exit(1)
    try:
        addr, vals = parse_read_holding_response(resp)
    except Exception as e:  # pragma: no cover
        print(f"bad response: {e}")
        sys.exit(3)
    print(f"addr={addr} vals={vals}")


if __name__ == "__main__":
    main()
