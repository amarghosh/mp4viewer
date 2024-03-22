#!/usr/bin/env python3
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

from mp4viewer.datasource import DataBuffer

class DataBufferTest:
    def __init__(self, path):
        self.path = path
        self.data_buffer = None

    def run(self):
        with open(self.path, 'rb') as f:
            self.data_buffer = DataBuffer(f)

            actual = self.data_buffer.readint32()
            value = 0xA5A5A5A5
            assert actual == value, f"Expected {value:x}, got {actual:x}"

            actual = self.data_buffer.readint64()
            value = 0xA5A5A5A5A5A5A5A5
            assert actual == value, f"Expected {value:x}, got {actual:x}"

            self.checkreadbits(32, 0xA5A5A5A5)
            self.checkreadbits(16, 0xA5A5)
            self.checkreadbits(8, 0xA5)
            self.checkreadbits(4, 0xA)
            self.checkreadbits(4, 0x5)
            self.checkreadbits(4, 0xA)
            self.checkreadbits(8, 0x5A)
            self.checkreadbits(24, 0x5A5A5A)
            self.checkreadbits(28, 0x5A5A5A5)
            self.checkreadbits(3, 5)
            self.checkreadbits(3, 1)
            self.checkreadbits(2, 1)
            self.checkreadbits(3, 5)
            self.checkreadbits(12, 0x2D2)
            self.checkreadbits(1, 1)
            self.checkreadbits(5, 0x14)
            self.checkreadbits(30, 0x2D2D2D2D)

    def checkreadbits(self, count, value):
        actual = self.data_buffer.readbits(count)
        assert actual == value, f"Expected 0x{value:X}, got 0x{actual:X}"


if __name__ == '__main__':
    # The file is a sequence of 0xA5 bytes
    dbt = DataBufferTest('tests/1.dat')
    dbt.run()
    print("Success")
