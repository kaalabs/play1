import math
from firmware.master.scale_service import ScaleService
from firmware.master.aggregator_service import get_status
from firmware.master import scale_halfdecent as hd


def _hd_frame(weight_g: int, stable: bool = True):
    b = bytearray([0x03, 0xCE if stable else 0xCA, 0x00, 0x00, 0x00, 0x00, 0x00])
    w = weight_g & 0xFFFF
    b[2] = (w >> 8) & 0xFF
    b[3] = w & 0xFF
    b[-1] = hd.xor_checksum(bytes(b))
    return bytes(b)


def test_flow_derivative_and_aggregate():
    svc = ScaleService(alpha=1.0, stable_up=1, stable_down=1)
    # Feed two frames with synthetic timestamps 0s and 2s, weights 0g -> 20g
    svc.on_notify(_hd_frame(0, True), t_s=0.0)
    r = svc.on_notify(_hd_frame(20, True), t_s=2.0)
    assert r and abs(r['flow_gps'] - 10.0) < 1e-6

    cur = svc.reading()
    dash = get_status(level_pct=33.0, tank_state='ok', weight_g=cur['weight_g'], stable=cur['stable'], source=cur['source'], flow_gps=cur['flow_gps'])
    assert 'tank' in dash and 'scale' in dash
    assert math.isclose(dash['scale']['flow_gps'], 10.0, rel_tol=1e-6)
