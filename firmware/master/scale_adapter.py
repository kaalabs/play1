"""Unified scale protocol adapter for Bookoo and Half Decent scales.

Produces a normalized dict:
- weight_g: float
- stable: bool
- source: 'bookoo' | 'halfdecent'
- meta: protocol-specific fields (optional: flow_gps, battery_pct, ms, smoothing)
"""

from typing import Optional, Dict, Any

from . import scale_bookoo as bookoo
from . import scale_halfdecent as hd


def decode(frame: bytes) -> Optional[Dict[str, Any]]:
    # Try Bookoo first (distinct 20B frame)
    if bookoo.is_weight_frame(frame):
        d = bookoo.parse_weight_frame(frame)
        if d is None:
            return None
        weight_g = float(d['weight_g'])
        flow = float(d.get('flow_gps', 0.0))
        stable = abs(flow) < 1e-3
        meta = {
            'flow_gps': d.get('flow_gps'),
            'battery_pct': d.get('battery_pct'),
            'ms': d.get('ms'),
            'smoothing': d.get('smoothing'),
        }
        return {
            'source': 'bookoo',
            'weight_g': weight_g,
            'stable': stable,
            'meta': meta,
        }

    # Try Half Decent (7 or 10 bytes)
    if hd.is_weight_packet(frame):
        d = hd.parse_weight(frame)
        if d is None:
            return None
        weight_g = float(d['weight_g'])
        stable = d.get('type') == 'CE'
        meta = {}
        if 'time' in d:
            meta['time'] = d['time']
        return {
            'source': 'halfdecent',
            'weight_g': weight_g,
            'stable': stable,
            'meta': meta,
        }

    return None


def build_tare(source: str, *, keep_heartbeat: bool = True) -> Optional[bytes]:
    if source == 'bookoo':
        return bookoo.cmd_tare()
    if source == 'halfdecent':
        return hd.cmd_tare(keep_heartbeat=keep_heartbeat)
    return None
