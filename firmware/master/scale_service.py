"""Scale service: consumes BLE notifications, normalizes via adapter, smooths, and exposes RPC.

Non-blocking, pure-Python logic suitable for MicroPython/CPython.
"""

from typing import Optional, Dict, Any, Deque, Tuple
from collections import deque
import time

from .scale_adapter import decode as decode_frame, build_tare


class WeightEMA:
    def __init__(self, alpha: float = 0.2):
        self.alpha = max(0.0, min(1.0, float(alpha)))
        self._y: Optional[float] = None

    def update(self, x: Optional[float]) -> Optional[float]:
        if x is None:
            return self._y
        if self._y is None:
            self._y = float(x)
        else:
            a = self.alpha
            self._y = a * float(x) + (1.0 - a) * self._y
        return self._y

    @property
    def value(self) -> Optional[float]:
        return self._y


class StabilityDebouncer:
    def __init__(self, up: int = 3, down: int = 3):
        self.up = max(1, int(up))
        self.down = max(1, int(down))
        self._stable = False
        self._cnt = 0
        self._last_obs = False

    def update(self, observed_stable: bool) -> bool:
        if observed_stable == self._last_obs:
            self._cnt += 1
        else:
            self._cnt = 1
            self._last_obs = observed_stable

        if self._stable:
            # currently stable; require 'down' consecutive unstable to flip
            if not observed_stable and self._cnt >= self.down:
                self._stable = False
        else:
            # currently unstable; require 'up' consecutive stable to flip
            if observed_stable and self._cnt >= self.up:
                self._stable = True
        return self._stable

    @property
    def value(self) -> bool:
        return self._stable


class ScaleService:
    def __init__(self, alpha: float = 0.2, stable_up: int = 3, stable_down: int = 3, history: int = 20):
        self.ema = WeightEMA(alpha)
        self.deb = StabilityDebouncer(stable_up, stable_down)
        self.source: Optional[str] = None
        self.meta: Dict[str, Any] = {}
        self._hist: Deque[Tuple[float, float]] = deque(maxlen=max(2, int(history)))  # (t_s, weight_g)

    def on_notify(self, frame: bytes, t_s: Optional[float] = None) -> Optional[Dict[str, Any]]:
        d = decode_frame(frame)
        if not d:
            return None
        self.source = d.get('source')
        w = float(d.get('weight_g', 0.0))
        smoothed = self.ema.update(w)
        stable = self.deb.update(bool(d.get('stable')))
        self.meta = d.get('meta') or {}
        # timebase: use provided t_s or try protocol meta or fallback to monotonic
        if t_s is None:
            if 'ms' in self.meta and isinstance(self.meta['ms'], (int, float)):
                t_s = float(self.meta['ms']) / 1000.0
            else:
                t_s = time.monotonic()
        self._hist.append((t_s, float(self.ema.value if self.ema.value is not None else w)))
        return {
            'weight_g': smoothed if smoothed is not None else w,
            'stable': stable,
            'source': self.source,
            'flow_gps': self.flow_gps(),
        }

    def reading(self) -> Dict[str, Any]:
        return {
            'weight_g': float(self.ema.value or 0.0),
            'stable': bool(self.deb.value),
            'source': self.source,
            'flow_gps': self.flow_gps(),
        }

    def flow_gps(self) -> float:
        if len(self._hist) < 2:
            return 0.0
        t0, w0 = self._hist[0]
        t1, w1 = self._hist[-1]
        dt = max(1e-6, t1 - t0)
        return (w1 - w0) / dt


def handle_cmd(cmd: str, svc: ScaleService, **kwargs) -> Dict[str, Any]:
    if cmd == 'get_weight':
        return svc.reading()
    if cmd == 'tare':
        src = kwargs.get('source') or svc.source
        if not src:
            return {'error': 'no_source'}
        keep = bool(kwargs.get('keep_heartbeat', True))
        b = build_tare(src, keep_heartbeat=keep)
        if not b:
            return {'error': 'unsupported_source'}
        return {
            'cmd': 'tare',
            'bytes_hex': b.hex(),
            'len': len(b),
        }
    return {'error': 'unknown_command'}
