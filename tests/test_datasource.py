#!/usr/bin/env python3
"""
Use xxd to edit binary files. It lets you convert between binary and hexdump formats

# 1.dat
00000000: a5a5 5a5a a5a5 a5a5 a5a5 a5a5 a5a5 a5a5  ..ZZ............
00000010: a5a5 a5a5 a5a5 a5a5 a5a5 a5a5 a5a5 a5a5  ................
00000020: a5a5 a5a5 ff6d 7034 7669 6577 6572 00a5  .....mp4viewer..
00000030: a5a5 a5a5 a5a5 a5a5 a5a5 a5a5 a5a5 a5a5  ................

"""
# pylint: disable=too-many-statements


from mp4viewer.datasource import DataBuffer, FileSource


class DataBufferTest:
    """Test DataBuffer and FileSource classes"""

    def __init__(self, file):
        self.buf = DataBuffer(FileSource(file))

    def run(self):
        """check various read functions"""
        buf = self.buf
        assert len(buf) == 64, f"Length is {len(buf)}"

        # First word is a5a5, second word is 5a5a, everything else is a5 until 36
        actual = buf.readint32()
        assert actual == 0xA5A55A5A, actual
        assert buf.current_position() == 4

        buf.reset()
        assert buf.current_position() == 0
        assert buf.readint16() == 0xA5A5
        # 5A is Z
        assert buf.readstr(2) == "ZZ"

        actual = buf.readint64()
        assert buf.current_position() == 12
        assert actual == 0xA5A5A5A5A5A5A5A5, actual

        # Test read bits
        # multiples of 8
        self.checkreadbits(32, 0xA5A5A5A5)
        self.checkreadbits(16, 0xA5A5)
        self.checkreadbits(8, 0xA5)
        assert buf.current_position() == 19

        # byte as two nibbles
        self.checkreadbits(4, 0xA)
        self.checkreadbits(4, 0x5)
        assert buf.current_position() == 20

        # read bits across bytes
        self.checkreadbits(4, 0xA)
        self.checkreadbits(8, 0x5A)
        self.checkreadbits(24, 0x5A5A5A)
        self.checkreadbits(28, 0x5A5A5A5)

        # smaller number of bits
        self.checkreadbits(3, 5)
        self.checkreadbits(3, 1)
        self.checkreadbits(2, 1)

        # 3 + 12 + 1
        self.checkreadbits(3, 5)
        self.checkreadbits(12, 0x2D2)
        self.checkreadbits(1, 1)

        # validate bit_position
        self.checkreadbits(5, 0x14)
        assert buf.bit_position == 5
        self.checkreadbits(30, 0x2D2D2D2D)
        assert buf.bit_position == 3
        buf.readbits(5)

        assert buf.bit_position == 0
        assert buf.current_position() == 36

        # next byte shall be 0xff
        assert buf.readbyte() == 0xFF
        assert buf.remaining_bytes() == 27, str(buf)

        # strings
        assert buf.readstr(3) == "mp4"
        buf.seekto(buf.current_position() - 3)
        # null terminated string
        cstr = buf.read_cstring()
        assert cstr[0] == "mp4viewer"
        assert cstr[1] == 10
        assert buf.current_position() == 47, buf.current_position()

        # cstring with max-length
        buf.seekto(buf.current_position() - 10)
        assert buf.read_cstring(3) == ("mp4", 3)

        # skip viewer\0 and the last remaining 0xa5
        buf.skipbytes(8)
        assert buf.remaining_bytes() == 16
        assert buf.current_position() == 48

        # readbytes
        a5bytes = buf.readbytes(8)
        for x in a5bytes:
            assert x == 0xA5

        buf.skipbytes(8)
        assert buf.remaining_bytes() == 0
        assert buf.current_position() == 64

    def checkreadbits(self, count, value):
        """read `count` bits and check the value"""
        actual = self.buf.readbits(count)
        assert actual == value, f"Expected 0x{value:X}, got 0x{actual:X}"


def test_datasource():
    """Test datasource"""
    with open("tests/1.dat", "rb") as f:
        dbt = DataBufferTest(f)
        dbt.run()
    print("Success")


if __name__ == "__main__":
    test_datasource()
