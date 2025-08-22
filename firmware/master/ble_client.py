"""BLE subscription helpers for master node.

Includes:
- FakeBleScale: test/simulation helper that invokes a callback with frames
- Optional Bleak-based scaffold (CPython) guarded by import

Note: We do not make bleak a hard dependency; code paths import it lazily.
"""

import time
from typing import Callable, Iterable, Optional


NotifyCb = Callable[[bytes], None]


class FakeBleScale:
    """Simulate BLE notifications by calling a callback with provided frames.

    Useful for dev/testing without hardware.
    """

    def __init__(self, frames: Iterable[bytes], interval_s: float = 0.05):
        self.frames = list(frames)
        self.interval_s = float(interval_s)

    def run(self, on_notify: NotifyCb):
        for f in self.frames:
            on_notify(f)
            time.sleep(self.interval_s)


def bleak_subscribe(address: str, notify_uuid: str, on_notify: NotifyCb) -> None:
    """Subscribe to a notify characteristic using bleak (if available).

    Minimal scaffold; not exercised in unit tests to avoid runtime deps.
    """
    try:
        import asyncio
        from bleak import BleakClient
    except Exception as e:  # pragma: no cover - optional path
        raise RuntimeError("bleak not available: install bleak to use this helper") from e

    async def _run():
        async with BleakClient(address) as client:
            async def _cb(_h, data: bytearray):
                on_notify(bytes(data))
            await client.start_notify(notify_uuid, _cb)
            # Run until cancelled; in real use, manage lifecycle externally
            while True:
                await asyncio.sleep(1.0)

    asyncio.run(_run())
