from firmware.core.modbus_rtu import crc16, build_adu, SimpleSlave
from firmware.master.modbus_master import build_read_holding, parse_read_holding_response


def test_crc16_known_vector():
    # Standard test: 0x01 0x03 0x00 0x00 0x00 0x0A -> CRC 0xC5CD (LSB first CD C5)
    data = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x0A])
    assert crc16(data) == 0xC5CD


def test_slave_read_holding_roundtrip():
    # Setup a simple map
    regs = list(range(0, 20))

    def read_cb(start, count):
        if start + count > len(regs):
            return False, ()
        return True, tuple(regs[start:start + count])

    def write_cb(start, values):
        return True

    slave = SimpleSlave(1, read_cb, write_cb)
    req = build_read_holding(1, 0, 4)
    resp = slave.feed_uart(req)
    assert resp is not None
    addr, vals = parse_read_holding_response(resp)
    assert addr == 1 and vals == (0, 1, 2, 3)
