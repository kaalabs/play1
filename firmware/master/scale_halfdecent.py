"""Half Decent Scale (HDS) BLE protocol helpers.

References: decentespresso/openscale
- Service UUID: 0000fff0-0000-1000-8000-00805f9b34fb
- Read Characteristic (notifications): 0000fff4-0000-1000-8000-00805f9b34fb
- Write Characteristic (commands):     000036f5-0000-1000-8000-00805f9b34fb

Weight notifications:
- 7-byte frame: [0]=0x03, [1]=0xCE or 0xCA, [2..3]=weight (int16 grams, BE), [4]=0x00, [5]=0x00, [6]=checksum
- 10-byte frame (fw >= 1.2): [0]=0x03, [1]=0xCE/0xCA, [2..3]=weight (int16 grams, BE), [4..6]=time bytes (m,s,ms?), [7]=0x00, [8]=0x00, [9]=checksum

Checksum: XOR starting from 0x03 over bytes [1..n-2].
"""

from typing import Optional, Dict, Any


SERVICE_UUID = '0000fff0-0000-1000-8000-00805f9b34fb'
CHAR_READ = '0000fff4-0000-1000-8000-00805f9b34fb'
CHAR_WRITE = '000036f5-0000-1000-8000-00805f9b34fb'


def xor_checksum(payload: bytes) -> int:
    if len(payload) < 2:
        return 0
    x = 0x03
    for b in payload[1:-1]:  # exclude first (we seed with 0x03) and last (checksum placeholder)
        x ^= b
    return x & 0xFF


def _valid_7b(pkt: bytes) -> bool:
    return (
        len(pkt) == 7
        and pkt[0] == 0x03
        and pkt[1] in (0xCE, 0xCA)
        and xor_checksum(pkt) == pkt[-1]
    )


def _valid_10b(pkt: bytes) -> bool:
    return (
        len(pkt) == 10
        and pkt[0] == 0x03
        and pkt[1] in (0xCE, 0xCA)
        and xor_checksum(pkt) == pkt[-1]
    )


def is_weight_packet(pkt: bytes) -> bool:
    return _valid_7b(pkt) or _valid_10b(pkt)


def parse_weight(pkt: bytes) -> Optional[Dict[str, Any]]:
    """Parse a 7- or 10-byte weight packet.
    Returns dict with weight_g, type ('CE' stable or 'CA' changing), and optional time tuple.
    """
    if not is_weight_packet(pkt):
        return None
    typ = 'CE' if pkt[1] == 0xCE else 'CA'
    w = (pkt[2] << 8) | pkt[3]
    # int16 signed big-endian
    if w & 0x8000:
        w = -((~w & 0xFFFF) + 1)
    weight_g = float(w)
    info: Dict[str, Any] = {
        'weight_g': weight_g,
        'type': typ,
    }
    if len(pkt) == 10:
        info['time'] = (pkt[4], pkt[5], pkt[6])  # minute, second, millisecond (as per doc examples)
    return info


def cmd_tare(keep_heartbeat: bool = True) -> bytes:
    """Build a 7-byte tare command.
    Old: 03 0F 00 00 00 00 0C (disables heartbeat)
    New: 03 0F 00 00 00 01 0D (leaves heartbeat as set)
    """
    b = bytearray(7)
    b[0] = 0x03
    b[1] = 0x0F
    b[2] = 0x00
    b[3] = 0x00
    b[4] = 0x00
    b[5] = 0x01 if keep_heartbeat else 0x00
    b[6] = xor_checksum(b)
    return bytes(b)
