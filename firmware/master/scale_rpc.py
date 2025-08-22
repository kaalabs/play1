"""Line-based RPC for the ScaleService.

Commands:
- get_weight -> { weight_g, flow_gps, stable, source }
- tare [keep_heartbeat?] -> returns hex bytes to write to BLE
"""

import json
import sys
import time
from typing import Optional

from .scale_service import ScaleService, handle_cmd


def rpc_loop(sample_period_s: float = 0.05):
    svc = ScaleService()
    last_emit = 0.0
    while True:
        # Non-blocking poll of stdin for commands
        line = sys.stdin.readline()
        if not line:
            time.sleep(sample_period_s)
            continue
        parts = line.strip().split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == 'tare':
            keep = True
            if len(parts) > 1:
                keep = parts[1].lower() in ('1', 'true', 'yes', 'y')
            out = handle_cmd('tare', svc, keep_heartbeat=keep)
        elif cmd == 'get_weight':
            out = handle_cmd('get_weight', svc)
        else:
            out = {'error': 'unknown_cmd'}
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()


if __name__ == '__main__':
    rpc_loop()
