
import os

class DataBuffer:
    CHUNK_SIZE = 50
    def __init__(self, stream):
        self.bit_position = 0
        self.stream_offset = 0
        self.buf_size = 0
        self.read_ptr = 0
        self.data = ''
        self.source = stream
        self.readmore()

    def __str__(self):
        return "<datasource size %d, readptr %d, offset %d>" %(
            self.buf_size, self.read_ptr, self.stream_offset)

    def readmore(self, minimum = 0):
        req_bytes = max(minimum, DataBuffer.CHUNK_SIZE)
        data = self.source.read(req_bytes)
        remaining_bytes = self.buf_size - self.read_ptr
        if len(data):
            # print "Read %d" %(len(data))
            self.data = self.data[self.read_ptr:] + data
            self.buf_size = remaining_bytes + len(data)
            self.stream_offset += self.read_ptr
            self.read_ptr = 0
            if self.buf_size < minimum:
                raise Exception("Not enough data for %d bytes; read %d, remaining %d",
                    minimum, len(data), self.buf_size)
        else:
            # print "Min %d, size %d, pos %d, offset %d" %(
            #    min, self.buf_size, self.read_ptr, self.stream_offset)
            raise Exception("Read nothing: req %d, offset %d, read_ptr %d",
                minimum, self.stream_offset, self.read_ptr)

    def hasmore(self):
        import traceback
        if self.read_ptr == self.buf_size:
            try:
                self.readmore()
            except:
                pass
        return self.read_ptr < self.buf_size

    def checkbuffer(self, length):
        if length < 0:
            raise Exception("Negative bytes to check %d" %(length))
        remaining_bytes = self.buf_size - self.read_ptr
        if remaining_bytes < length:
            self.readmore(length - remaining_bytes)
            remaining_bytes = self.buf_size - self.read_ptr

        if remaining_bytes < length:
            raise Exception("Attempt to read beyond buffer %d %d %d", self.read_ptr, self.buf_size, length)

    def peekstr(self, length, offset = 0):
        self.checkbuffer(length + offset)
        if self.bit_position:
            raise Exception("Not aligned: %d" %self.bit_position)
        return str(self.data[self.read_ptr + offset:self.read_ptr + offset + length])

    def readstr(self, length):
        s = self.peekstr(length)
        self.read_ptr += length
        return s

    def read_cstring(self, max_length=-1):
        if self.bit_position:
            raise Exception("Not aligned: %d" %self.bit_position)
        # TODO: Handle utf8
        s = ''
        bytes_read = 0
        while self.hasmore():
            if bytes_read == max_length:
                break
            c = self.readbyte()
            bytes_read += 1
            if not c:
                break
            s += chr(c)
        return s, bytes_read

    def peekint(self, bytecount):
        self.checkbuffer(bytecount)
        if self.bit_position:
            raise Exception("Not aligned: %d" %self.bit_position)
        v = 0
        for i in range(0, bytecount):
            v = v << 8 | ord(self.data[self.read_ptr + i])
        return v

    def peekbits(self, bitcount):
        bytes_req = (bitcount + self.bit_position) / 8
        bytes_req += 1 if (bitcount + self.bit_position) % 8 else 0
        self.checkbuffer(bytes_req)
        if bitcount > 32:
            raise Exception("%d bits?!! Use readint64() and do your own bit manipulations!" %(bitcount))
        if not (0 <= self.bit_position < 8):
            raise Exception("bit_position %d" %self.bit_position)
        byte_offset = 0
        bits_read = 0
        result = 0
        while bits_read != bitcount:
            result <<= 8
            result |= ord(self.data[self.read_ptr + byte_offset])
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
        res = self.peekbits(bitcount)
        self.read_ptr += (bitcount + self.bit_position) / 8
        self.bit_position = (self.bit_position + bitcount) % 8
        return res

    def readint(self, bytecount):
        v = self.peekint(bytecount)
        self.read_ptr += bytecount
        return v

    def readbyte(self):
        return self.readint(1)

    def readint16(self):
        return self.readint(2)

    def readint32(self):
        return self.readint(4)

    def readint64(self):
        return self.readint(8)

    def skipbytes(self, count):
        if self.bit_position:
            raise Exception("Not aligned: %d" %self.bit_position)
        if count < 0:
            raise Exception("Negative bytes to skip %d" %(count))
        remaining_bytes = self.buf_size - self.read_ptr
        if count < remaining_bytes:
            self.read_ptr += count
        else:
            # TODO: would this seek beyond?
            self.source.seek(count - remaining_bytes, os.SEEK_CUR)
            self.data = ''
            self.stream_offset += self.read_ptr + count
            self.buf_size = 0
            self.read_ptr = 0

