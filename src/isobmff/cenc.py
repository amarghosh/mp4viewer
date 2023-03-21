from __future__ import absolute_import

import sys
from . import box

class TrackEncryptionBox(box.FullBox):
    def parse(self, buf):
        super(TrackEncryptionBox, self).parse(buf)
        buf.skipbytes(1)
        if self.version == 0:
            buf.skipbytes(1)
        else:
            val = buf.readbyte()
            self.default_crypt_byte_block = (val & 0xf0) >> 4
            self.default_skip_byte_block = val & 0x0f
        self.default_isProtected = buf.readbyte() == 1
        self.default_Per_Sample_IV_size = buf.readbyte()
        self.default_KID = []
        for i in range(16):
            self.default_KID.append(buf.readbyte())
        if self.default_isProtected == 1 and self.default_Per_Sample_IV_size == 0:
            self.default_constant_IV_size = buf.readbyte()
            self.default_constant_IV = []
            for i in range(self.default_constant_IV_size):
                self.default_constant_IV.append(buf.readbyte())
    
    def generate_fields(self):
        for x in super(TrackEncryptionBox, self).generate_fields():
            yield x
        if self.version != 0:
            yield ("Default crypt byte block", self.default_crypt_byte_block)
            yield ("Default skip byte block", self.default_skip_byte_block)
        yield ("Default is protected", self.default_isProtected)
        yield ("Default KID", "0x" + "%x" * 16 %tuple(self.default_KID))
        if self.default_isProtected == 1 and self.default_Per_Sample_IV_size == 0:
            yield ("Default constant IV size", self.default_constant_IV_size)
            yield ("Default constant IV", 
                    "0x"+ "%x" * self.default_constant_IV_size
                    %tuple(self.default_constant_IV))


class ProtectionSystemSpecificHeader(box.FullBox):
    def parse(self, buf):
        super(ProtectionSystemSpecificHeader, self).parse(buf)
        self.system_id = []
        for i in range(16):
            self.system_id.append(buf.readbyte())
        if self.version > 0:
            self.KID_count = buf.readint32()
            self.KIDs = []
            for i in range(self.KID_count):
                KID = []
                for j in range(16):
                    KID.append(buf.readbyte())
                self.KIDs.append(KID)
        self.data_size = buf.readint32()
        buf.skipbytes(self.data_size)
    
    def generate_fields(self):
        for x in super(ProtectionSystemSpecificHeader, self).generate_fields():
            yield x
        yield ("System ID", "0x" + "%x" * 16 %tuple(self.system_id))
        if self.version > 0:
            yield ("KID count", self.KID_count)
            for k in self.KIDs:
                yield ("KID", "0x" + "%x" * 16 %tuple(k))
        yield ("Data Size", self.data_size)


class SchemeTypeBox(box.FullBox):
    def parse(self, buf):
        super(SchemeTypeBox, self).parse(buf)
        self.scheme_type = buf.readstr(4)
        self.scheme_version = buf.readint32()
        if self.flags & 0x000001:
            self.consumed_bytes += 8
            self.scheme_uri = buf.read_cstring(self.size - self.consumed_bytes)[0]
    
    def generate_fields(self):
        for x in super(SchemeTypeBox, self).generate_fields():
            yield x
        yield ("Scheme type", self.scheme_type)
        yield ("Scheme version", "0x%x" %(self.scheme_version))
        if self.flags & 0x000001:
            yield ("Scheme URI", self.scheme_uri)


class OriginalFormatBox(box.Box):
    def parse(self, buf):
        super(OriginalFormatBox, self).parse(buf)
        self.data_format = buf.readstr(4)
    
    def generate_fields(self):
        for x in super(OriginalFormatBox, self).generate_fields():
            yield x
        yield ("Original format", self.data_format)


boxmap = {
        'tenc' : TrackEncryptionBox,
        # senc can't be used without guesswork/heroics/the creation of a 'root'
        # box because it needs the 'tenc' box which is in the moov header,
        # while this is in the moof header.  They do not share a parent.
        #'senc' : SampleEncryptionBox,
        'pssh' : ProtectionSystemSpecificHeader,
        'schm' : SchemeTypeBox,
        'frma' : OriginalFormatBox,
        }
