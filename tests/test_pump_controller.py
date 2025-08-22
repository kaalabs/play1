import time

from firmware.core.pump_controller import PumpController
from firmware.core.hal_stub import HAL


def test_pump_runs_on_brew_switch_and_stops():
    hal = HAL()
    c = PumpController(hal)
    t0 = time.time()
    # Start
    s, r = c.tick(t0, brew_switch=True)
    assert s == "run" and r is None and hal.pump_state is True
    # Continue
    s, r = c.tick(t0 + 1, brew_switch=True)
    assert s == "run" and hal.pump_state is True
    # Stop
    s, r = c.tick(t0 + 2, brew_switch=False)
    assert s == "idle" and hal.pump_state is False


def test_min_rest_inhibits_immediate_restart():
    hal = HAL()
    c = PumpController(hal)
    t0 = time.time()
    # Start and stop quickly
    c.tick(t0, brew_switch=True)
    c.tick(t0 + 1, brew_switch=False)
    # Try restart within min rest
    s, r = c.tick(t0 + c.cfg.min_rest_s - 1, brew_switch=True)
    assert s == "inhibit" and r == "rest" and hal.pump_state is False


def test_rate_limit():
    hal = HAL()
    c = PumpController(hal)
    t0 = time.time()
    for i in range(c.cfg.max_starts_per_min):
        c.tick(t0 + i * 10, brew_switch=True)
        c.tick(t0 + i * 10 + 1, brew_switch=False)
    # Next start within one minute window should inhibit
    s, r = c.tick(t0 + 59, brew_switch=True)
    assert s == "inhibit" and r == "rate_limit" and hal.pump_state is False


def test_timeout_fault():
    hal = HAL()
    c = PumpController(hal)
    t0 = time.time()
    c.tick(t0, brew_switch=True)
    # Exceed max_run_s
    s, r = c.tick(t0 + c.cfg.max_run_s + 1, brew_switch=True)
    assert s == "fault" and r == "pump_run_timeout" and hal.pump_state is False
