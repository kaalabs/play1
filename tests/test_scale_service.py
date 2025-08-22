from firmware.master.scale_service import ScaleService, handle_cmd
from firmware.master import scale_bookoo as bk
from firmware.master import scale_halfdecent as hd


def _bk_frame(weight_g: float, flow_gps: float = 0.0):
    w_raw = int(abs(weight_g) * 100)
    w_hi, w_mid, w_lo = (w_raw >> 16) & 0xFF, (w_raw >> 8) & 0xFF, w_raw & 0xFF
    f_raw = int(abs(flow_gps) * 100)
    f_hi, f_lo = (f_raw >> 8) & 0xFF, f_raw & 0xFF
    ms = 10
    base = bytearray(20)
    base[0] = 0x03
    base[1] = 0x0B
    base[2] = 0
    base[3] = 0
    base[4] = ms
    base[5] = 0
    base[6] = 1 if weight_g < 0 else 0
    base[7] = w_hi
    base[8] = w_mid
    base[9] = w_lo
    base[10] = 1 if flow_gps < 0 else 0
    base[11] = f_hi
    base[12] = f_lo
    base[13] = 80
    base[14] = 0
    base[15] = 5
    base[16] = 0
    base[17] = 0
    base[18] = 0
    base[19] = bk.xor_checksum(bytes(base[:-1]))
    return bytes(base)


def _hd_frame(weight_g: int, stable: bool = True):
    b = bytearray([0x03, 0xCE if stable else 0xCA, 0x00, 0x00, 0x00, 0x00, 0x00])
    # signed 16-bit grams
    w = weight_g & 0xFFFF
    b[2] = (w >> 8) & 0xFF
    b[3] = w & 0xFF
    b[-1] = hd.xor_checksum(bytes(b))
    return bytes(b)


def test_service_smoothing_and_stability():
    svc = ScaleService(alpha=0.5, stable_up=2, stable_down=2)

    # Two changing frames -> unstable
    svc.on_notify(_hd_frame(100, stable=False))
    r1 = svc.on_notify(_hd_frame(100, stable=False))
    assert r1 and r1['stable'] is False

    # Two stable frames -> becomes stable
    svc.on_notify(_hd_frame(100, stable=True))
    r2 = svc.on_notify(_hd_frame(100, stable=True))
    assert r2 and r2['stable'] is True

    # Bookoo frame with flow -> should flip to unstable after two
    svc.on_notify(_bk_frame(100.0, 0.2))
    r3 = svc.on_notify(_bk_frame(100.0, 0.2))
    assert r3 and r3['stable'] is False

    # Smoothed weight present
    now = svc.reading()
    assert 'weight_g' in now and isinstance(now['weight_g'], float)


def test_handle_cmds():
    svc = ScaleService()
    # No source yet
    out = handle_cmd('tare', svc)
    assert 'error' in out

    # After a notify, source is known
    svc.on_notify(_hd_frame(0, stable=True))
    out2 = handle_cmd('tare', svc, keep_heartbeat=False)
    assert out2.get('cmd') == 'tare' and out2.get('len') == 7

    # Get reading
    out3 = handle_cmd('get_weight', svc)
    assert 'weight_g' in out3 and 'stable' in out3
