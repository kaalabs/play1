"""Example runner that feeds ScaleService from a fake BLE stream.

Use this for local smoke tests; on device, wire real BLE notifications and call svc.on_notify().
"""

import json
from .scale_service import ScaleService
from .ble_client import FakeBleScale
from . import scale_halfdecent as hd


def _demo_frames():
    # stable 0g to 50g
    for w in (0, 10, 20, 30, 40, 50):
        b = bytearray([0x03, 0xCE, 0x00, 0x00, 0, 0, 0])
        b[2] = (w >> 8) & 0xFF
        b[3] = w & 0xFF
        b[-1] = hd.xor_checksum(bytes(b))
        yield bytes(b)


def main():
    svc = ScaleService()
    fake = FakeBleScale(_demo_frames(), interval_s=0.01)

    def on_notify(frame: bytes):
        out = svc.on_notify(frame)
        if out:
            print(json.dumps(out))

    fake.run(on_notify)


if __name__ == '__main__':
    main()
