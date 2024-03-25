#!/usr/bin/env python3
"""Test box parsing"""

from functools import reduce

from mp4viewer.datasource import DataBuffer, FileSource
from mp4viewer.isobmff.parser import IsobmffParser


def _string_to_fourcc_int(s):
    return reduce(lambda a, b: (a << 8) + b, [ord(x) for x in s], 0)


def test_ftyp():
    """ftyp box"""
    with open("tests/ftyp.mp4.dat", "rb") as fd:
        parser = IsobmffParser(DataBuffer(FileSource(fd)))
        boxes = parser.getboxlist()
        assert len(boxes) == 1
        ftyp_box = boxes[0]
        assert ftyp_box.boxtype == "ftyp"
        assert ftyp_box.size == 24
        assert ftyp_box.major_brand == "mp42"
        assert ftyp_box.minor_version == 1
        assert len(ftyp_box.brands) == 2
        assert ftyp_box.brands[0] == "mp42"
        assert ftyp_box.brands[1] == "avc1"
        assert parser.buf.remaining_bytes() == 0
        assert len(list(ftyp_box.generate_fields())) > 0


def test_moov():
    """moov and its children"""
    with open("tests/moov.mp4.dat", "rb") as fd:
        parser = IsobmffParser(DataBuffer(FileSource(fd)))
        boxes = parser.getboxlist()
        assert len(boxes) == 1
        moov = boxes[0]
        assert moov.boxtype == "moov"
        assert moov.size == 116
        assert len(moov.children) == 1
        mvhd = moov.children[0]
        assert mvhd.boxtype == "mvhd"
        assert mvhd.size == 108
        assert mvhd.creation_time == 3531256179
        assert mvhd.modification_time == 3531256179
        assert mvhd.timescale == 1000
        assert mvhd.duration == 5096
        assert mvhd.rate == 0x10000
        assert mvhd.volume == 0x100
        for i in range(3):
            for j in range(3):
                if i == j and i < 2:
                    assert mvhd.matrix[i][j] == 0x10000
                elif i == 2 and j == 2:
                    assert mvhd.matrix[i][j] == 0x40000000
                else:
                    assert mvhd.matrix[i][j] == 0, f"{i},{j}={mvhd.matrix[i][j]}"
        assert mvhd.next_track_id == 0
        assert len(list(moov.generate_fields())) > 0
        assert len(list(mvhd.generate_fields())) > 0


if __name__ == "__main__":
    test_ftyp()
    test_moov()
