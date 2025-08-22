from firmware.master.scale_halfdecent import (
    xor_checksum,
    is_weight_packet,
    parse_weight,
    cmd_tare,
)


def test_checksum_examples():
    # Stable 7-byte frame: 03 CE 01 F4 00 00 CS (500.0g)
    pkt = bytearray([0x03, 0xCE, 0x01, 0xF4, 0x00, 0x00, 0x00])
    pkt[-1] = xor_checksum(bytes(pkt))
    pkt = bytes(pkt)
    assert xor_checksum(pkt) == pkt[-1]
    assert is_weight_packet(pkt)

    # Changing 7-byte frame: 03 CA FF 9C 00 00 CS (-10.0g)
    pkt2 = bytearray([0x03, 0xCA, 0xFF, 0x9C, 0x00, 0x00, 0x00])
    pkt2[-1] = xor_checksum(bytes(pkt2))
    pkt2 = bytes(pkt2)
    assert xor_checksum(pkt2) == pkt2[-1]
    assert is_weight_packet(pkt2)


def test_parse_weight_values_7b():
    # 500.0g stable
    pkt = bytearray([0x03, 0xCE, 0x01, 0xF4, 0x00, 0x00, 0x00])
    pkt[-1] = xor_checksum(bytes(pkt))
    d = parse_weight(bytes(pkt))
    assert d is not None
    assert d['type'] == 'CE'
    assert abs(d['weight_g'] - 500.0) < 1e-6

    # -100.0g changing
    pkt2 = bytearray([0x03, 0xCA, 0xFF, 0x9C, 0x00, 0x00, 0x00])
    pkt2[-1] = xor_checksum(bytes(pkt2))
    d2 = parse_weight(bytes(pkt2))
    assert d2 is not None
    assert d2['type'] == 'CA'
    assert abs(d2['weight_g'] - (-100.0)) < 1e-6


def test_parse_weight_values_10b():
    # Hypothetical 10-byte packet: 03 CE 00 64 00 01 32 00 00 CS
    base = bytearray([0x03, 0xCE, 0x00, 0x64, 0x00, 0x01, 0x32, 0x00, 0x00, 0x00])
    from firmware.master.scale_halfdecent import xor_checksum as _xc

    base[-1] = _xc(base)
    d = parse_weight(bytes(base))
    assert d is not None
    assert d['type'] == 'CE'
    assert abs(d['weight_g'] - 100.0) < 1e-6
    assert d.get('time') == (0x00, 0x01, 0x32)


def test_cmd_tare_checksum_and_flag():
    c1 = cmd_tare(True)
    assert len(c1) == 7
    assert c1[0] == 0x03 and c1[1] == 0x0F
    assert c1[5] == 0x01
    assert xor_checksum(c1) == c1[-1]

    c2 = cmd_tare(False)
    assert c2[5] == 0x00
    assert xor_checksum(c2) == c2[-1]
