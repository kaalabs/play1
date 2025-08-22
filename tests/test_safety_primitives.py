from firmware.common.safety import FaultLatch, Watchdog, RateLimiter
import time


def test_fault_latch():
    f = FaultLatch()
    assert not f.tripped
    f.trip("x")
    assert f.tripped and f.reason == "x"
    f.clear()
    assert not f.tripped


def test_watchdog():
    w = Watchdog(timeout_s=0.05)
    w.kick()
    assert not w.expired()
    time.sleep(0.06)
    assert w.expired()


def test_rate_limiter():
    r = RateLimiter(min_interval_s=0.05)
    assert r.allow()
    assert not r.allow()
    time.sleep(0.06)
    assert r.allow()
