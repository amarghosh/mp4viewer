
import os

class DataBuffer:
    CHUNK_SIZE = 50
    def __init__(self, stream):
        self.stream_offset = 0
        self.buf_size = 0
        self.read_ptr = 0
        self.data = ''
        self.source = stream
        self.readmore()

    def __str__(self):
        return "<datasource size %d, readptr %d, offset %d>" %(self.buf_size, self.read_ptr, self.stream_offset)

    def readmore(self, min = 0):
        req_bytes = max(min, DataBuffer.CHUNK_SIZE)
        data = self.source.read(req_bytes)
        remaining_bytes = self.buf_size - self.read_ptr
        if len(data):
            # print "Read %d" %(len(data))
            self.data = self.data[self.read_ptr:] + data
            self.buf_size = remaining_bytes + len(data)
            self.stream_offset += self.read_ptr
            self.read_ptr = 0
        else:
            # print "Min %d, size %d, pos %d, offset %d" %(min, self.buf_size, self.read_ptr, self.stream_offset)
            raise Exception("read nothing")

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
        return str(self.data[self.read_ptr + offset:self.read_ptr + offset + length])

    def readstr(self, length):
        s = self.peekstr(length)
        self.read_ptr += length
        return s

    def peekint(self, bytecount):
        self.checkbuffer(bytecount)
        v = 0
        for i in range(0, bytecount):
            v = v << 8 | ord(self.data[self.read_ptr + i])
        return v

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

