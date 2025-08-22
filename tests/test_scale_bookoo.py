from firmware.master.scale_bookoo import (
    xor_checksum,
    is_weight_frame,
    parse_weight_frame,
    cmd_tare,
    cmd_set_beep,
    cmd_set_auto_off,
    cmd_timer_start,
    cmd_timer_stop,
    cmd_timer_reset,
    cmd_tare_and_start,
    cmd_set_flow_smoothing,
)


def make_weight_frame(ms=123456, weight_g=12.34, flow_gps=0.56, battery=87, unit_code=0, w_sign=0, f_sign=0,
                      standby_min=10, buzzer=1, smoothing=1):
    ms_hi = (ms >> 16) & 0xFF
    ms_mid = (ms >> 8) & 0xFF
    ms_lo = ms & 0xFF
    w_raw = int(abs(weight_g) * 100)
    f_raw = int(abs(flow_gps) * 100)
    frame = bytearray(20)
    frame[0] = 0x03
    frame[1] = 0x0B
    frame[2] = ms_hi
    frame[3] = ms_mid
    frame[4] = ms_lo
    frame[5] = unit_code
    frame[6] = 1 if weight_g < 0 else w_sign
    frame[7] = (w_raw >> 16) & 0xFF
    frame[8] = (w_raw >> 8) & 0xFF
    frame[9] = w_raw & 0xFF
    frame[10] = 1 if flow_gps < 0 else f_sign
    frame[11] = (f_raw >> 8) & 0xFF
    frame[12] = f_raw & 0xFF
    frame[13] = battery
    frame[14] = (standby_min >> 8) & 0xFF
    frame[15] = standby_min & 0xFF
    frame[16] = buzzer
    frame[17] = smoothing
    frame[18] = 0
    frame[19] = xor_checksum(frame[:-1])
    return bytes(frame)


def test_parse_weight_frame_basic():
    f = make_weight_frame()
    assert is_weight_frame(f)
    parsed = parse_weight_frame(f)
    assert parsed is not None
    assert abs(parsed['weight_g'] - 12.34) < 0.01
    assert abs(parsed['flow_gps'] - 0.56) < 0.01


def test_commands_checksum_lengths():
    for b in [
        cmd_tare(),
        cmd_set_beep(3),
        cmd_set_auto_off(10),
        cmd_timer_start(),
        cmd_timer_stop(),
        cmd_timer_reset(),
        cmd_tare_and_start(),
        cmd_set_flow_smoothing(True),
        cmd_set_flow_smoothing(False),
    ]:
        assert len(b) == 6
        assert xor_checksum(b[:-1]) == b[-1]
