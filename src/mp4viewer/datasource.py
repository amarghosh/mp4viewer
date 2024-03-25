""" Defines data buffer related classes """

import os
from typing import BinaryIO


class FileSource:
    """Read isobmff data from a file"""

    def __init__(self, f: BinaryIO):
        self.file = f
        self.size = os.fstat(f.fileno()).st_size

    def read(self, req_bytes):
        """read up to req_bytes"""
        return self.file.read(req_bytes)

    def seek(self, count, pos):
        """wrapper around file.seek"""
        return self.file.seek(count, pos)

    def __len__(self):
        return self.size


class DataBuffer:
    """
    Class represending a data buffer.
    Provides helper functions to read uint32, UTF8 strings etc from the buffer.
    """

    CHUNK_SIZE = 16384

    def __init__(self, source):
        self.source = source

        # Chunk of bytes loaded from the source stream for convenience.
        # This is a sub-sequence of the byte stream managed by self.source.
        self.data = b""

        # length of current `data`; this can vary across calls to readmore
        self.buf_size = 0

        # Offset within `source` that matches the first byte of self.data
        self.stream_offset = 0

        # Number of bytes that has been consumed so far from `self.data`
        self.read_ptr = 0

        # Number of bits consumed from the current byte (data[read_ptr])
        self.bit_position = 0

        self._reset()
        self.readmore()

    def reset(self):
        """reset everything"""
        self.source.seek(0, os.SEEK_SET)
        self._reset()

    def _reset(self):
        """reset internal offsets, doesn't touch the source"""
        self.bit_position = 0
        self.stream_offset = 0
        self.buf_size = 0
        self.read_ptr = 0
        self.data = b""

    def __str__(self):
        # pylint: disable=consider-using-f-string
        return "<datasource size %d, buf=%d readptr %d, offset %d>" % (
            len(self.source),
            self.buf_size,
            self.read_ptr,
            self.stream_offset,
        )

    def current_position(self):
        """return the current offset of the buffer from the beginning of the `source`"""
        return self.stream_offset + self.read_ptr

    def remaining_bytes(self):
        """Return the number of bytes remaining to read"""
        return len(self.source) - (self.stream_offset + self.read_ptr)

    def readmore(self, minimum=0):
        # pylint: disable=consider-using-f-string
        """
        Read some bytes from the source in to local data array.
        If minimum is set, this will try to read at least that many bytes
        """
        req_bytes = max(minimum, DataBuffer.CHUNK_SIZE)
        data = self.source.read(req_bytes)
        remaining_bytes = self.buf_size - self.read_ptr
        if len(data):
            # print(f"Read {len(data)}")
            self.data = b"".join([self.data[self.read_ptr :], data])
            self.buf_size = remaining_bytes + len(data)
            self.stream_offset += self.read_ptr
            self.read_ptr = 0
            if self.buf_size < minimum:
                raise AssertionError(
                    "Not enough data for %d bytes; read %d, remaining %d"
                    % (minimum, len(data), self.buf_size)
                )
        else:
            raise AssertionError(
                "Read nothing: req %d, offset %d, read_ptr %d"
                % (minimum, self.stream_offset, self.read_ptr)
            )

    def hasmore(self) -> bool:
        """return true if we have bytes remaining to be read from the source"""
        if self.read_ptr == self.buf_size:
            try:
                self.readmore()
            except AssertionError:
                pass
        return self.read_ptr < self.buf_size

    def checkbuffer(self, length):
        """
        Ensure that the buffer has at least length bytes available to read.
        Throws ValueError if there aren't enough bytes left.
        """
        if length < 0:
            raise ValueError(f"Negative bytes to check {length}")
        remaining_bytes = self.buf_size - self.read_ptr
        if remaining_bytes < length:
            self.readmore(length - remaining_bytes)
            remaining_bytes = self.buf_size - self.read_ptr

        if remaining_bytes < length:
            # pylint: disable=consider-using-f-string
            raise ValueError(
                "Attempt to read beyond buffer %d %d %d"
                % (self.read_ptr, self.buf_size, length)
            )

    def peekstr(self, length, offset=0):
        """read a string of `length` bytes without updating the buffer pointer"""
        self.checkbuffer(length + offset)
        if self.bit_position:
            raise AssertionError(f"Not aligned: {self.bit_position}")
        return str(
            self.data[self.read_ptr + offset : self.read_ptr + offset + length], "utf-8"
        )

    def readstr(self, length):
        """read a string of `length` bytes and update the buffer pointer"""
        s = self.peekstr(length)
        self.read_ptr += length
        return s

    def read_cstring(self, max_length=-1):
        """
        Read a null ternimated string of max_length bytes and return a tuple with two elements:
        the string, and the number of bytes consumed.
        """
        if self.bit_position:
            raise AssertionError(f"Not aligned: {self.bit_position}")
        str_bytes = bytearray()
        s = ""
        bytes_read = 0
        while self.hasmore():
            if bytes_read == max_length:
                break
            c = self.readbyte()
            bytes_read += 1
            if not c:
                break
            str_bytes.append(c)
        s = str_bytes.decode("utf-8")
        return s, bytes_read

    def peekint(self, bytecount):
        """
        Read a number of specified bytes from the stream without updating the current position
        """
        self.checkbuffer(bytecount)
        if self.bit_position:
            raise AssertionError(f"Not aligned: {self.bit_position}")
        v = 0
        for i in range(0, bytecount):
            data_byte = self.data[self.read_ptr + i]
            v = v << 8 | data_byte
        return v

    def peekbits(self, bitcount):
        """read `bitcount` bits without moving the pointer"""
        bytes_req = (bitcount + self.bit_position) // 8
        bytes_req += 1 if (bitcount + self.bit_position) % 8 else 0
        self.checkbuffer(bytes_req)
        if bitcount > 32:
            raise AssertionError(f"{bitcount} bits? Use readint64() and DIY")
        if not 0 <= self.bit_position < 8:
            raise AssertionError(f"bit_position {self.bit_position}")
        byte_offset = 0
        bits_read = 0
        result = 0
        while bits_read != bitcount:
            result <<= 8
            data_byte = self.data[self.read_ptr + byte_offset]
            result |= data_byte
            byte_offset += 1
            if bits_read == 0 and self.bit_position != 0:
                result &= (1 << (8 - self.bit_position)) - 1
                bits_read += 8 - self.bit_position
            else:
                bits_read += 8
            if bits_read > bitcount:
                result >>= bits_read - bitcount
                bits_read = bitcount
        return result

    def readbits(self, bitcount):
        """read the next `bitcount` bits and return it as an integer"""
        res = self.peekbits(bitcount)
        self.read_ptr += (bitcount + self.bit_position) // 8
        self.bit_position = (self.bit_position + bitcount) % 8
        return res

    def readbytes(self, count):
        """read `count` bytes from the stream and return it as a list of ints"""
        return [self.readbyte() for i in range(count)]

    def readint(self, bytecount):
        """read an integer of `bytecount` bytes from the stream"""
        v = self.peekint(bytecount)
        self.read_ptr += bytecount
        return v

    def readbyte(self):
        """read one byte from the current position and return it as an int"""
        return self.readint(1)

    def readint16(self):
        """read a 16 bit integer from the current position"""
        return self.readint(2)

    def readint32(self):
        """read a 32 bit integer from the current position"""
        return self.readint(4)

    def readint64(self):
        """read a 64 bit integer from the current position"""
        return self.readint(8)

    def skipbytes(self, count):
        """
        Skip `count` bytes.
        The read position should be aligned to the nearest byte before you call this.
        You can use readbits to discard any remaining bits from the current byte to accomplish this.
        """
        if self.bit_position:
            raise AssertionError(f"Not aligned: {self.bit_position}")
        if count < 0:
            raise ValueError(f"Negative bytes to skip {count}")
        unread_loaded_bytes = self.buf_size - self.read_ptr
        if count < unread_loaded_bytes:
            self.read_ptr += count
            return

        if self.current_position() + count > len(self.source):
            overflow = (self.current_position() + count) - len(self)
            available_to_skip = len(self.source)
            raise BufferError(
                f"{self} consumed={self.current_position()} skipping {count} "
                f"bytes would cause overflow {overflow} available={available_to_skip}"
            )

        self.source.seek(count - unread_loaded_bytes, os.SEEK_CUR)
        new_stream_offset = self.stream_offset + self.read_ptr + count
        self._reset()
        self.stream_offset = new_stream_offset

    def seekto(self, pos):
        """Move the read pointer to to `pos`, relative to the start of stream"""
        self.source.seek(pos, os.SEEK_SET)
        self._reset()
        self.stream_offset = pos
        self.readmore()

    def __len__(self):
        return len(self.source)
