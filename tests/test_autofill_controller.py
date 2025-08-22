import time

from firmware.core.autofill_controller import AutofillController


class AutofillHAL:
    def __init__(self):
        self.valve_state = False

    def fill_valve(self, on: bool):
        self.valve_state = bool(on)


def test_autofill_ok_to_fill_and_timeout():
    hal = AutofillHAL()
    c = AutofillController(hal)

    t0 = time.time()
    # Low level -> fill
    state, reason = c.tick(t0, probe_wet=False)
    assert state == "fill" and reason is None and hal.valve_state is True

    # Continue filling until timeout
    state, reason = c.tick(t0 + c.cfg.fill_timeout_s + 0.1, probe_wet=False)
    assert state == "fault" and reason == "fill_timeout" and hal.valve_state is False


def test_autofill_rate_limit():
    hal = AutofillHAL()
    c = AutofillController(hal)
    t0 = time.time()

    # First low -> fill a bit
    s, _ = c.tick(t0, probe_wet=False)
    assert s == "fill"

    # Level returns (wet)
    s, _ = c.tick(t0 + 1, probe_wet=True)
    assert s == "ok"

    # Immediately low again -> inhibit by rate limit
    s, r = c.tick(t0 + 2, probe_wet=False)
    assert s == "inhibit" and r == "rate_limit" and hal.valve_state is False
