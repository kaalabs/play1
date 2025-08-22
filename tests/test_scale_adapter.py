from firmware.master.scale_adapter import decode, build_tare
from firmware.master import scale_bookoo as bk
from firmware.master import scale_halfdecent as hd


def _bk_frame(weight_g: float, flow_gps: float = 0.0, battery: int = 80, ms: int = 123456, smoothing: bool = False):
    w_raw = int(abs(weight_g) * 100)
    w_hi, w_mid, w_lo = (w_raw >> 16) & 0xFF, (w_raw >> 8) & 0xFF, w_raw & 0xFF
    f_raw = int(abs(flow_gps) * 100)
    f_hi, f_lo = (f_raw >> 8) & 0xFF, f_raw & 0xFF
    ms_hi, ms_mid, ms_lo = (ms >> 16) & 0xFF, (ms >> 8) & 0xFF, ms & 0xFF
    w_sign = 1 if weight_g < 0 else 0
    f_sign = 1 if flow_gps < 0 else 0
    base = bytearray(20)
    base[0] = 0x03
    base[1] = 0x0B
    base[2] = ms_hi
    base[3] = ms_mid
    base[4] = ms_lo
    base[5] = 0  # grams
    base[6] = w_sign
    base[7] = w_hi
    base[8] = w_mid
    base[9] = w_lo
    base[10] = f_sign
    base[11] = f_hi
    base[12] = f_lo
    base[13] = battery
    base[14] = 0
    base[15] = 5
    base[16] = 0
    base[17] = 1 if smoothing else 0
    base[18] = 0
    base[19] = bk.xor_checksum(bytes(base[:-1]))
    return bytes(base)


def test_decode_bookoo_frames():
    f = _bk_frame(17.3, 0.0)
    d = decode(f)
    assert d and d['source'] == 'bookoo'
    assert abs(d['weight_g'] - 17.3) < 1e-6
    assert d['stable'] is True

    f2 = _bk_frame(10.0, 0.55)
    d2 = decode(f2)
    assert d2 and d2['source'] == 'bookoo'
    assert d2['stable'] is False


def test_decode_halfdecent_frames():
    pkt = bytearray([0x03, 0xCE, 0x01, 0xF4, 0x00, 0x00, 0x00])  # 500g stable
    pkt[-1] = hd.xor_checksum(bytes(pkt))
    d = decode(bytes(pkt))
    assert d and d['source'] == 'halfdecent'
    assert abs(d['weight_g'] - 500.0) < 1e-6
    assert d['stable'] is True

    pkt2 = bytearray([0x03, 0xCA, 0xFF, 0x9C, 0x00, 0x00, 0x00])  # -100g changing
    pkt2[-1] = hd.xor_checksum(bytes(pkt2))
    d2 = decode(bytes(pkt2))
    assert d2 and d2['source'] == 'halfdecent'
    assert abs(d2['weight_g'] - (-100.0)) < 1e-6
    assert d2['stable'] is False


def test_build_tare():
    t1 = build_tare('bookoo')
    assert isinstance(t1, (bytes, bytearray)) and len(t1) == 6
    assert bk.xor_checksum(t1[:-1]) == t1[-1]

    t2 = build_tare('halfdecent', keep_heartbeat=False)
    assert isinstance(t2, (bytes, bytearray)) and len(t2) == 7
    assert hd.xor_checksum(t2) == t2[-1]