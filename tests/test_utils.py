from firmware.common.utils import Linearizer


def test_linearizer_basic():
    lin = Linearizer([(0.0, 0.0), (10.0, 100.0)])
    assert lin(-1.0) == 0.0
    assert lin(0.0) == 0.0
    assert lin(5.0) == 50.0
    assert lin(10.0) == 100.0
    assert lin(11.0) == 100.0
