""" track encryption related boxes """

from . import box


class TrackEncryptionBox(box.FullBox):
    """tenc"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        buf.skipbytes(1)
        if self.version == 0:
            buf.skipbytes(1)
        else:
            val = buf.readbyte()
            self.default_crypt_byte_block = (val & 0xF0) >> 4
            self.default_skip_byte_block = val & 0x0F
        self.default_is_protected = buf.readbyte() == 1
        self.default_per_sample_iv_size = buf.readbyte()
        self.default_kid = []
        for _ in range(16):
            self.default_kid.append(buf.readbyte())
        if self.default_is_protected == 1 and self.default_per_sample_iv_size == 0:
            self.default_constant_iv_size = buf.readbyte()
            self.default_constant_iv = []
            for _ in range(self.default_constant_iv_size):
                self.default_constant_iv.append(buf.readbyte())

    def generate_fields(self):
        super().generate_fields()
        if self.version != 0:
            yield ("Default crypt byte block", self.default_crypt_byte_block)
            yield ("Default skip byte block", self.default_skip_byte_block)
        yield ("Default is protected", self.default_is_protected)
        yield ("Default per sample IV size", self.default_constant_iv_size)
        yield ("Default KID", [f"{i:02x}" for i in range(self.default_kid)])
        if self.default_is_protected == 1 and self.default_per_sample_iv_size == 0:
            yield ("Default constant IV size", self.default_constant_iv_size)
            yield (
                "Default constant IV",
                [f"{i:02x}" for i in range(self.default_constant_iv)],
            )


class ProtectionSystemSpecificHeader(box.FullBox):
    """pssh"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        self.system_id = []
        for _ in range(16):
            self.system_id.append(buf.readbyte())
        if self.version > 0:
            self.kid_count = buf.readint32()
            self.kids = []
            for _ in range(self.kid_count):
                kid = [buf.readbyte() for _ in range(16)]
                self.kids.append(kid)
        self.data_size = buf.readint32()
        buf.skipbytes(self.data_size)

    def generate_fields(self):
        super().generate_fields()
        yield ("System ID", "0x" + "%x" * 16 % tuple(self.system_id))
        if self.version > 0:
            yield ("KID count", self.kid_count)
            for kid in self.kids:
                yield ("KID", ["f{i:02x}" for i in kid])
        yield ("Data Size", self.data_size)


class SchemeTypeBox(box.FullBox):
    """schm"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        self.scheme_type = buf.readstr(4)
        self.scheme_version = buf.readint32()
        if self.flags & 0x000001:
            self.consumed_bytes += 8
            self.scheme_uri = buf.read_cstring(self.size - self.consumed_bytes)[0]

    def generate_fields(self):
        super().generate_fields()
        yield ("Scheme type", self.scheme_type)
        yield ("Scheme version", f"0x{self.scheme_version:x}")
        if self.flags & 0x000001:
            yield ("Scheme URI", self.scheme_uri)


class OriginalFormatBox(box.Box):
    """frma"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        self.data_format = buf.readstr(4)

    def generate_fields(self):
        super().generate_fields()
        yield ("Original format", self.data_format)


boxmap = {
    "tenc": TrackEncryptionBox,
    # senc can't be used without guesswork/heroics/the creation of a 'root'
    # box because it needs the 'tenc' box which is in the moov header,
    # while this is in the moof header.  They do not share a parent.
    # 'senc' : SampleEncryptionBox,
    "pssh": ProtectionSystemSpecificHeader,
    "schm": SchemeTypeBox,
    "frma": OriginalFormatBox,
}
