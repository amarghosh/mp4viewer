#!/usr/bin/env python3
"""Test box parsing"""

from functools import reduce

from mp4viewer.datasource import DataBuffer, FileSource
from mp4viewer.isobmff.parser import IsobmffParser


def _string_to_fourcc_int(s):
    return reduce(lambda a, b: (a << 8) + b, [ord(x) for x in s], 0)


def test_ftyp():
    """ftyp box"""
    with open("tests/ftyp.atom", "rb") as fd:
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


def _validate_matrix_values(matrix):
    # All 3x3 matrixes are set to the following
    # 0x10000   0           0
    # 0         0x10000     0
    # 0         0           0x40000000
    for i in range(3):
        for j in range(3):
            if i == j and i < 2:
                assert matrix[i][j] == 0x10000
            elif i == 2 and j == 2:
                assert matrix[i][j] == 0x40000000
            else:
                assert matrix[i][j] == 0, f"{i},{j}={matrix[i][j]}"


def _validate_movie_header_box(mvhd):
    assert mvhd.boxtype == "mvhd"
    assert mvhd.size == 108
    assert mvhd.creation_time == 3531256179
    assert mvhd.modification_time == 3531256179
    assert mvhd.timescale == 1000
    assert mvhd.duration == 5096
    assert mvhd.rate == 0x10000
    assert mvhd.volume == 0x100
    assert mvhd.next_track_id == 0
    _validate_matrix_values(mvhd.matrix)
    assert len(list(mvhd.generate_fields())) > 0


def _validate_trak_1(trak):
    assert trak.boxtype == "trak"
    assert trak.size == 0x88
    assert len(trak.children) == 2
    _validate_tkhd_1(trak.children[0])
    _validate_edts(trak.children[1])


def _validate_edts(edts):
    assert edts.boxtype == "edts"
    assert edts.size == 0x24
    assert len(edts.children) == 1
    elst = edts.children[0]
    assert len(elst.entries) == 1
    entry = elst.entries[0]
    assert entry["segment_duration"] == 37026990
    assert entry["media_time"] == 3003
    assert entry["media_rate_integer"] == 1
    assert entry["media_rate_fraction"] == 0


def _validate_tkhd_1(tkhd):
    assert tkhd.boxtype == "tkhd"
    assert tkhd.size == 0x5C
    assert tkhd.flags == 7
    assert tkhd.creation_time == 3531256179
    assert tkhd.modification_time == 3531256179
    assert tkhd.track_id == 1
    assert tkhd.duration == 5096
    assert tkhd.layer == 0xBB
    assert tkhd.altgroup == 0xAA00
    assert tkhd.volume == 0x0010
    _validate_matrix_values(tkhd.matrix)
    assert tkhd.width == 0x05A00000
    assert tkhd.height == 0x05A00000


def test_moov():
    """moov and its children"""
    with open("tests/moov.atom", "rb") as fd:
        parser = IsobmffParser(DataBuffer(FileSource(fd)))
        boxes = parser.getboxlist()
        assert len(boxes) == 1
        moov = boxes[0]
        assert moov.boxtype == "moov"
        assert moov.size == 0xFC
        assert len(moov.children) == 2, moov.children
        assert len(list(moov.generate_fields())) > 0
        mvhd = moov.children[0]
        _validate_movie_header_box(mvhd)
        trak = moov.children[1]
        _validate_trak_1(trak)


if __name__ == "__main__":
    test_ftyp()
    test_moov()
