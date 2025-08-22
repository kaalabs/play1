import time

from firmware.core.boiler_controller import BoilerController
from firmware.core.hal_stub import HAL


def test_hysteresis_basic():
    hal = HAL()
    c = BoilerController(hal)

    t0 = time.time()
    # Low pressure -> heat
    state, reason = c.tick(t0, p_bar=0.5, autofill_active=False)
    assert state == "heat" and reason is None
    assert hal.heater_state is True

    # Within band -> hold
    state, _ = c.tick(t0 + 1, p_bar=c.cfg.target_bar, autofill_active=False)
    assert state in ("hold", "idle")

    # High pressure -> idle
    state, _ = c.tick(t0 + 2, p_bar=c.cfg.target_bar + c.cfg.hysteresis_bar + 0.05)
    assert state == "idle"
    assert hal.heater_state is False


def test_autofill_inhibits_heating():
    hal = HAL()
    c = BoilerController(hal)
    t0 = time.time()
    state, reason = c.tick(t0, p_bar=0.5, autofill_active=True)
    assert state == "inhibit" and reason == "autofill"
    assert hal.heater_state is False


def test_sensor_plausibility_fault():
    hal = HAL()
    c = BoilerController(hal)
    t0 = time.time()
    state, reason = c.tick(t0, p_bar=10.0, autofill_active=False)
    assert state == "fault" and reason == "sensor_out_of_range"
    assert hal.heater_state is False
