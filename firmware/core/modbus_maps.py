"""Register maps for core nodes.

Conventions (Holding Registers 0x03):
- 0x0000: status code (0=idle/ok, 1=run/fill, 2=inhibit, 3=fault)
- 0x0001: reason code (implementation-defined small ints)
- 0x0002: tank_ok (0/1)
- 0x0003: reserved
"""

from typing import Tuple


class PumpMap:
    def __init__(self):
        self.reg = [0] * 16

    def read(self, start: int, count: int) -> Tuple[bool, Tuple[int, ...]]:
        if start + count > len(self.reg):
            return False, ()
        return True, tuple(self.reg[start:start + count])

    def write(self, start: int, values: Tuple[int, ...]) -> bool:
        if start + len(values) > len(self.reg):
            return False
        # For now, accept writes only to reserved area (e.g., control commands could be added)
        for i, v in enumerate(values):
            if start + i >= 8:
                self.reg[start + i] = v & 0xFFFF
        return True


class AutofillMap(PumpMap):
    pass


class BoilerMap(PumpMap):
    pass
