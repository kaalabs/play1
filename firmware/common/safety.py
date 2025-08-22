# Safety primitives for autonomous core nodes
# Portable subset for MicroPython and CPython (tests)

import time


class LatchingFault(Exception):
    pass


class FaultLatch:
    def __init__(self):
        self._fault = None

    @property
    def tripped(self) -> bool:
        return self._fault is not None

    @property
    def reason(self):
        return self._fault

    def trip(self, reason: str):
        if not self._fault:
            self._fault = reason

    def clear(self):
        self._fault = None


class Watchdog:
    def __init__(self, timeout_s: float):
        self.timeout_s = timeout_s
        self._last_kick = time.time()

    def kick(self):
        self._last_kick = time.time()

    def expired(self) -> bool:
        return (time.time() - self._last_kick) > self.timeout_s


class RateLimiter:
    def __init__(self, min_interval_s: float):
        self.min_interval_s = min_interval_s
        self._last_time = 0.0

    def allow(self) -> bool:
        now = time.time()
        if now - self._last_time >= self.min_interval_s:
            self._last_time = now
            return True
        return False
