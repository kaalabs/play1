"""Aggregator service: composes tank and scale readings for a dashboard-friendly RPC.

This is pure assembly; tank logic lives in tank_service and scale logic in scale_service.
"""

from typing import Any, Dict


def get_status(*, level_pct: float, tank_state: str, weight_g: float, stable: bool, source: str = None, flow_gps: float = 0.0) -> Dict[str, Any]:
    return {
        'tank': {
            'level_pct': float(level_pct),
            'state': tank_state,
        },
        'scale': {
            'weight_g': float(weight_g),
            'flow_gps': float(flow_gps),
            'stable': bool(stable),
            'source': source,
        },
    }
