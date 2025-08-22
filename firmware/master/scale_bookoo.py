"""BooKoo Scale BLE protocol helpers (Mini/Themis family).

Based on BooKoo OpenSource docs:
- Service UUID: 0x0FFE
- Command Characteristic: 0xFF12
- Weight Data Characteristic: 0xFF11

Checksum: XOR of all bytes except the checksum (which is last byte).

Weight frame (20 bytes total):
[0]=0x03, [1]=0x0B, [2]=ms_hi, [3]=ms_mid, [4]=ms_lo,
[5]=unit_code, [6]=weight_sign, [7]=w_hi, [8]=w_mid, [9]=w_lo,
[10]=flow_sign, [11]=f_hi, [12]=f_lo, [13]=battery_pct,
[14]=standby_hi, [15]=standby_lo, [16]=buzzer, [17]=smoothing,
[18]=reserved(0), [19]=checksum

Weight in grams = (w_hi<<16 | w_mid<<8 | w_lo) / 100.0, apply sign if needed.
Flow (g/s) = (f_hi<<8 | f_lo) / 100.0, apply sign if needed.
"""

from typing import Optional, Dict, Any


SERVICE_UUID = 0x0FFE
CHAR_CMD_UUID = 0xFF12
CHAR_DATA_UUID = 0xFF11


def xor_checksum(b: bytes) -> int:
    c = 0
    for x in b:
        c ^= x
    return c & 0xFF


def is_weight_frame(frame: bytes) -> bool:
    return len(frame) == 20 and frame[0] == 0x03 and frame[1] == 0x0B and xor_checksum(frame[:-1]) == frame[-1]


def parse_weight_frame(frame: bytes) -> Optional[Dict[str, Any]]:
    if not is_weight_frame(frame):
        return None
    ms = (frame[2] << 16) | (frame[3] << 8) | frame[4]
    unit_code = frame[5]
    unit = 'g' if unit_code == 0 else 'g'  # protocol notes grams only
    w_sign = -1 if frame[6] else 1
    w_raw = (frame[7] << 16) | (frame[8] << 8) | frame[9]
    weight_g = w_sign * (w_raw / 100.0)
    f_sign = -1 if frame[10] else 1
    f_raw = (frame[11] << 8) | frame[12]
    flow_gps = f_sign * (f_raw / 100.0)
    battery = frame[13]
    standby_min = (frame[14] << 8) | frame[15]
    buzzer = frame[16]
    smoothing = bool(frame[17])
    return {
        'ms': ms,
        'unit': unit,
        'weight_g': weight_g,
        'flow_gps': flow_gps,
        'battery_pct': battery,
        'standby_min': standby_min,
        'buzzer': buzzer,
        'smoothing': smoothing,
    }


# Command frames: [0]=0x03, [1]=0x0A, [2]=cmd, [3]=data2, [4]=data3, [5]=checksum
def _cmd(cmd: int, d2: int = 0x00, d3: int = 0x00) -> bytes:
    base = bytes([0x03, 0x0A, cmd & 0xFF, d2 & 0xFF, d3 & 0xFF])
    cs = xor_checksum(base)
    return base + bytes([cs])


def cmd_tare() -> bytes:
    return _cmd(0x01, 0x00, 0x00)


def cmd_set_beep(level: int) -> bytes:
    level = max(0, min(5, int(level)))
    return _cmd(0x02, level, 0x00)


def cmd_set_auto_off(minutes: int) -> bytes:
    minutes = max(1, min(30, int(minutes)))
    return _cmd(0x03, minutes, 0x00)


def cmd_timer_start() -> bytes:
    return _cmd(0x04, 0x00, 0x00)


def cmd_timer_stop() -> bytes:
    return _cmd(0x05, 0x00, 0x00)


def cmd_timer_reset() -> bytes:
    return _cmd(0x06, 0x00, 0x00)


def cmd_tare_and_start() -> bytes:
    return _cmd(0x07, 0x00, 0x00)


def cmd_set_flow_smoothing(on: bool) -> bytes:
    return _cmd(0x08, 0x01 if on else 0x00, 0x00)
