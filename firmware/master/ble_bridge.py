"""Desktop BLE bridge for Bookoo and Half Decent scales (optional, uses bleak).

Features:
- Connects by BLE address or name, subscribes to weight notifications.
- Feeds frames into ScaleService and prints JSON readings to stdout.
- Reads stdin for simple commands like 'tare' and writes to the scale.

Usage (examples):
  python -m firmware.master.ble_bridge --source halfdecent --address AA:BB:CC:DD:EE:FF
  python -m firmware.master.ble_bridge --source bookoo --name "Themis"

Note: Requires 'bleak' on desktop. This is not a hard dependency of the project.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from typing import Optional

from .scale_service import ScaleService
from .scale_adapter import build_tare
from . import scale_bookoo as bk
from . import scale_halfdecent as hd


def _full_uuid(short: int) -> str:
    return f"0000{short:04x}-0000-1000-8000-00805f9b34fb"


def uuids_for_source(source: str):
    s = source.lower()
    if s == 'bookoo':
        notify = _full_uuid(bk.CHAR_DATA_UUID)
        write = _full_uuid(bk.CHAR_CMD_UUID)
        return notify, write
    if s == 'halfdecent':
        return hd.CHAR_READ, hd.CHAR_WRITE
    raise ValueError("unknown source: " + source)


async def _stdin_lines(loop: asyncio.AbstractEventLoop, q: asyncio.Queue[str]):
    def _blocking_readline():
        return sys.stdin.readline()
    while True:
        line = await loop.run_in_executor(None, _blocking_readline)
        if not line:
            await asyncio.sleep(0.05)
            continue
        await q.put(line.strip())


async def run_bridge(source: str, address: Optional[str], name: Optional[str]):
    try:
        from bleak import BleakClient, BleakScanner
    except Exception as e:  # pragma: no cover
        print("Error: bleak not installed. pip install bleak", file=sys.stderr)
        return 2

    notify_uuid, write_uuid = uuids_for_source(source)

    if not address:
        if not name:
            print("Error: provide --address or --name", file=sys.stderr)
            return 2
        print(f"Scanning for device name contains '{name}'...")
        devs = await BleakScanner.discover(timeout=5.0)
        cand = next((d for d in devs if d.name and name.lower() in d.name.lower()), None)
        if not cand:
            print("Error: device not found", file=sys.stderr)
            return 3
        address = cand.address
    print(f"Connecting to {address} ({source})")

    svc = ScaleService()
    q: asyncio.Queue[str] = asyncio.Queue()
    loop = asyncio.get_event_loop()
    asyncio.create_task(_stdin_lines(loop, q))

    async with BleakClient(address) as client:
        async def _cb(_h, data: bytearray):
            out = svc.on_notify(bytes(data))
            if out:
                print(json.dumps(out))
        await client.start_notify(notify_uuid, _cb)
        print("Subscribed; enter 'tare' to send tare.")
        try:
            while True:
                try:
                    line = await asyncio.wait_for(q.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue
                if not line:
                    continue
                parts = line.split()
                cmd = parts[0].lower()
                if cmd == 'tare':
                    keep = True
                    if len(parts) > 1:
                        keep = parts[1].lower() in ('1', 'true', 'yes', 'y')
                    frame = build_tare(source, keep_heartbeat=keep)
                    if frame:
                        await client.write_gatt_char(write_uuid, frame)
                        print(json.dumps({'sent': 'tare'}))
                else:
                    print(json.dumps({'error': 'unknown_cmd'}))
        finally:
            await client.stop_notify(notify_uuid)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--source', required=True, choices=['bookoo', 'halfdecent'])
    p.add_argument('--address', help='BLE MAC (Linux) or UUID (macOS)')
    p.add_argument('--name', help='Partial device name to scan for')
    args = p.parse_args(argv)
    return asyncio.run(run_bridge(args.source, args.address, args.name))


if __name__ == '__main__':
    raise SystemExit(main())
