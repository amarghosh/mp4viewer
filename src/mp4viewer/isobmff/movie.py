""" Movie and track related boxes """

# pylint: disable=too-many-instance-attributes

from . import box
from .utils import get_utc_from_seconds_since_1904
from .utils import parse_iso639_2_15bit
from .utils import stringify_duration
from .utils import error_print


class MovieHeader(box.FullBox):
    """mvhd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        if self.version == 1:
            self.creation_time = buf.readint64()
            self.modification_time = buf.readint64()
            self.timescale = buf.readint32()
            self.duration = buf.readint64()
        else:
            self.creation_time = buf.readint32()
            self.modification_time = buf.readint32()
            self.timescale = buf.readint32()
            self.duration = buf.readint32()
        self.rate = buf.readint32()
        self.volume = buf.readint16()
        buf.skipbytes(2 + 8)
        self.matrix = [[buf.readint32() for j in range(3)] for i in range(3)]
        buf.skipbytes(24)
        self.next_track_id = buf.readint32()

    def generate_fields(self):
        super().generate_fields()
        yield (
            "creation time",
            self.creation_time,
            get_utc_from_seconds_since_1904(self.creation_time).ctime(),
        )
        yield (
            "modification time",
            self.creation_time,
            get_utc_from_seconds_since_1904(self.modification_time).ctime(),
        )
        yield ("timescale", self.timescale)
        yield (
            "duration",
            self.duration,
            stringify_duration(self.duration / self.timescale),
        )
        yield ("rate", f"0x{self.rate:08X}")
        yield ("volume", f"0x{self.volume:04X}")
        yield ("matrix", self.matrix)
        yield ("next track id", self.next_track_id)


class TrackHeader(box.FullBox):
    """tkhd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        if self.version == 1:
            self.creation_time = buf.readint64()
            self.modification_time = buf.readint64()
            self.track_id = buf.readint32()
            buf.skipbytes(4)
            self.duration = buf.readint64()
        else:
            self.creation_time = buf.readint32()
            self.modification_time = buf.readint32()
            self.track_id = buf.readint32()
            buf.skipbytes(4)
            self.duration = buf.readint32()
        buf.skipbytes(8)
        self.layer = buf.readint16()
        self.altgroup = buf.readint16()
        self.volume = buf.readint16()
        buf.skipbytes(2)
        self.matrix = [[buf.readint32() for j in range(3)] for i in range(3)]
        self.width = buf.readint32()
        self.height = buf.readint32()

    def generate_fields(self):
        super().generate_fields()
        yield (
            "creation time",
            self.creation_time,
            get_utc_from_seconds_since_1904(self.creation_time).ctime(),
        )
        yield (
            "modification time",
            self.modification_time,
            get_utc_from_seconds_since_1904(self.modification_time).ctime(),
        )
        yield ("track id", self.track_id)
        mvhd = self.find_descendant_of_ancestor("moov", "mvhd")
        if mvhd is None:
            error_print("Failed to find movie header to decode track duration")
            yield ("duration", self.duration)
        else:
            yield (
                "duration",
                self.duration,
                stringify_duration(self.duration / mvhd.timescale),
            )
        yield ("layer", f"0x{self.layer:04X}")
        yield ("alternate group", f"0x{self.altgroup:04X}")
        yield ("volume", f"0x{self.volume:04X}")
        yield ("matrix", self.matrix)
        yield ("width", self.width)
        yield ("height", self.height)


class MediaHeader(box.FullBox):
    """mdhd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        if self.version == 1:
            self.creation_time = buf.readint64()
            self.modification_time = buf.readint64()
            self.timescale = buf.readint32()
            self.duration = buf.readint64()
        else:
            self.creation_time = buf.readint32()
            self.modification_time = buf.readint32()
            self.timescale = buf.readint32()
            self.duration = buf.readint32()
        self.language = buf.readint16() & 0x7FFF
        buf.skipbytes(2)

    def generate_fields(self):
        super().generate_fields()
        yield (
            "creation time",
            self.creation_time,
            get_utc_from_seconds_since_1904(self.creation_time).ctime(),
        )
        yield (
            "modification time",
            self.modification_time,
            get_utc_from_seconds_since_1904(self.modification_time).ctime(),
        )
        yield ("timescale", self.timescale)
        yield (
            "duration",
            self.duration,
            stringify_duration(self.duration / self.timescale),
        )
        yield ("language", self.language, parse_iso639_2_15bit(self.language))


class VideoMediaHeader(box.FullBox):
    """vmhd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.graphicsmode = buf.readint16()
        self.opcolor = []
        for _ in range(0, 3):
            self.opcolor.append(buf.readint16())

    def generate_fields(self):
        super().generate_fields()
        yield ("graphics mode", self.graphicsmode)
        yield ("opcolor", self.opcolor)


class SoundMediaHeader(box.FullBox):
    """smhd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.balance = buf.readint16()
        buf.skipbytes(2)

    def generate_fields(self):
        super().generate_fields()
        yield ("balance", self.balance)


class HintMediaHeader(box.FullBox):
    """hmhd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.max_pdu_size = buf.readint16()
        self.avg_pdu_size = buf.readint16()
        self.max_bitrate = buf.readint16()
        self.avg_bitrate = buf.readint16()

    def generate_fields(self):
        super().generate_fields()
        yield ("Max PDU size", self.max_pdu_size)
        yield ("Average PDU size", self.avg_pdu_size)
        yield ("Max bitrate", self.max_bitrate)
        yield ("Average bitrate", self.avg_bitrate)


class HandlerBox(box.FullBox):
    """hdlr"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        buf.skipbytes(4)
        self.handler = buf.readstr(4)
        buf.skipbytes(12)
        self.consumed_bytes += 20
        self.name = buf.read_cstring(self.size - self.consumed_bytes)[0]

    def generate_fields(self):
        super().generate_fields()
        yield ("handler", self.handler)
        yield ("name", self.name if len(self.name) else "<empty>")


class SampleEntry(box.Box):
    """base type for various sample entry classes"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        buf.skipbytes(6)
        self.data_ref_index = buf.readint16()
        self.consumed_bytes += 8

    def generate_fields(self):
        super().generate_fields()
        yield ("data reference index", self.data_ref_index)


class HintSampleEntry(SampleEntry):
    """???? (inside sample description when handler=hint)"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        buf.skipbytes(self.size - self.consumed_bytes)


class VisualSampleEntry(SampleEntry):
    """possibly avc1 (inside sample description when handler=vide)"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        buf.skipbytes(2 + 2 + 3 * 4)
        self.width = buf.readint16()
        self.height = buf.readint16()
        self.hori_resolution = buf.readint32()
        self.vert_resolution = buf.readint32()
        buf.skipbytes(4)
        self.frame_count = buf.readint16()
        compressor_name_length = buf.readbyte()
        self.compressor_name = (
            buf.readstr(compressor_name_length) if compressor_name_length else ""
        )
        buf.skipbytes(32 - compressor_name_length - 1)
        self.depth = buf.readint16()
        buf.skipbytes(2)
        self.has_children = True

    def generate_fields(self):
        super().generate_fields()
        yield ("width", self.width)
        yield ("height", self.height)
        yield ("horizontal resolution", f"0x{self.hori_resolution:08X}")
        yield ("vertical resolution", f"0x{self.vert_resolution:08X}")
        yield ("frame count", self.frame_count)
        yield ("compressor name", self.compressor_name)
        yield ("depth", self.depth)


class AudioSampleEntry(SampleEntry):
    """possibly mp4a (inside sample description when handler=soun)"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        # 14496-12 says first eight bits are reserved.
        # Apple QuickTime format (MOV) uses those bytes for version, revision and vendor
        # The size of this box in QT varies according to the version, so we need the version
        self.quicktime_version = buf.readint16()
        buf.skipbytes(6)
        self.channel_count = buf.readint16()
        self.sample_size = buf.readint16()
        buf.skipbytes(4)
        self.sample_rate = buf.readint32()
        if self.quicktime_version == 1:
            self.samples_per_pkt = buf.readint32()
            self.bytes_per_pkt = buf.readint32()
            self.bytes_per_frame = buf.readint32()
            self.bytes_per_sample = buf.readint32()
        elif self.quicktime_version == 2:
            buf.skipbytes(36)
        self.has_children = True

    def generate_fields(self):
        super().generate_fields()
        yield ("channel count", self.channel_count)
        yield ("sample size", self.sample_size)
        yield (
            "sample rate",
            self.sample_rate,
            f"{self.sample_rate >> 16}, {self.sample_rate & 0xFFFF}",
        )


class SampleDescription(box.FullBox):
    """stsd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        media = self.find_ancestor("mdia")
        hdlr = media.find_child("hdlr") if media else None
        handler = hdlr.handler if hdlr else None
        self.entry_count = buf.readint32()
        for _ in range(self.entry_count):
            if handler == "soun":
                self.children.append(AudioSampleEntry(parse_ctx))
            elif handler == "vide":
                self.children.append(VisualSampleEntry(parse_ctx))
            elif handler == "hint":
                self.children.append(HintSampleEntry(parse_ctx))
            else:
                entry = box.Box(parse_ctx)
                self.children.append(entry)
                buf.skipbytes(entry.size - entry.consumed_bytes)
        if len(self.children) != 0:
            self.has_children = True

    def generate_fields(self):
        super().generate_fields()
        yield ("entry count", self.entry_count)


class DataEntryUrnBox(box.FullBox):
    """'urn '"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.name = buf.read_cstring()[0]
        self.location = buf.read_cstring()[0]

    def generate_fields(self):
        super().generate_fields()
        yield ("name", self.name)
        yield ("location", self.location)


class DataEntryUrlBox(box.FullBox):
    """'url '"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.location = buf.read_cstring(self.size - self.consumed_bytes)[0]

    def generate_fields(self):
        super().generate_fields()
        yield ("location", self.location)


class DataReferenceBox(box.FullBox):
    """dref"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.entry_count = buf.readint32()
        self.has_children = True
        for _ in range(self.entry_count):
            self.children.append(parse_ctx.getnextbox(self))

    def generate_fields(self):
        super().generate_fields()
        yield ("entry count", self.entry_count)


class TimeToSampleBox(box.FullBox):
    """stts"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.entry_count = buf.readint32()
        self.entries = []
        for _ in range(self.entry_count):
            count = buf.readint32()
            delta = buf.readint32()
            self.entries.append((count, delta))

    def generate_fields(self):
        super().generate_fields()
        yield ("entry count", self.entry_count)
        for entry in self.entries:
            yield ("sample count", entry[0])
            yield ("sample delta", entry[1])


class SampleToChunkBox(box.FullBox):
    """stsc"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.entry_count = buf.readint32()
        self.entries = []
        for _ in range(self.entry_count):
            first = buf.readint32()
            samples_per_chunk = buf.readint32()
            sdix = buf.readint32()
            self.entries.append((first, samples_per_chunk, sdix))

    def generate_fields(self):
        super().generate_fields()
        yield ("entry count", self.entry_count)
        if self.entry_count > 10:
            yield (
                "chunk data hidden",
                f"{self.entry_count} entries can be toggled in movies.py/SampleToChunkBox",
            )
        else:
            for entry in self.entries:
                yield ("first chunk", entry[0])
                yield ("samples per chunk", entry[1])
                yield ("sample description index", entry[2])


class ChunkOffsetBox(box.FullBox):
    """stco"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.entry_count = buf.readint32()
        self.entries = [buf.readint32() for i in range(self.entry_count)]

    def generate_fields(self):
        super().generate_fields()
        yield ("entry count", self.entry_count)
        yield ("chunk offsets", self.entries)


class SyncSampleBox(box.FullBox):
    """stss"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.entry_count = buf.readint32()
        self.entries = [buf.readint32() for i in range(self.entry_count)]

    def generate_fields(self):
        super().generate_fields()
        yield ("entry count", self.entry_count)
        yield ("sample numbers", self.entries)


class SampleSizeBox(box.FullBox):
    """stsz"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.sample_size = buf.readint32()
        self.sample_count = buf.readint32()
        if self.sample_size == 0:
            self.entries = [buf.readint32() for i in range(self.sample_count)]
        else:
            self.entries = []

    def generate_fields(self):
        super().generate_fields()
        yield ("sample size", self.sample_size)
        yield ("sample count", self.sample_count)
        if self.sample_size == 0:
            yield ("sample sizes", self.entries)


class CompactSampleSizeBox(box.FullBox):
    """stz2"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        buf.skipbytes(3)
        self.field_size = buf.readbyte()
        self.sample_count = buf.readint32()
        self.entries = [buf.readbits(self.field_size) for i in range(self.sample_count)]
        # skip padding bits
        if self.field_size == 4 and self.sample_count % 2 != 0:
            buf.readbits(4)

    def generate_fields(self):
        super().generate_fields()
        yield ("field size", self.field_size)
        yield ("sample count", self.sample_count)
        yield ("entries", self.entries)


class MovieExtendsHeader(box.FullBox):
    """mehd"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        if self.version == 1:
            self.fragment_duration = buf.readint64()
        else:
            self.fragment_duration = buf.readint32()

    def generate_fields(self):
        super().generate_fields()
        yield ("Fragment duration", self.fragment_duration)


class TrackExtendsBox(box.FullBox):
    """trex"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.track_id = buf.readint32()
        self.default_sample_description_index = buf.readint32()
        self.default_sample_duration = buf.readint32()
        self.default_sample_size = buf.readint32()
        self.default_sample_flags = buf.readint32()

    def generate_fields(self):
        super().generate_fields()
        yield ("Track ID", self.track_id)
        yield (
            "Default sample description index",
            self.default_sample_description_index,
        )
        yield ("Default sample duration", self.default_sample_duration)
        yield ("Default sample size", self.default_sample_size)
        yield ("Default sample flags", self.default_sample_flags)


class AvcCBox(box.Box):
    """avcC"""

    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.configuration_level = buf.readbyte()
        self.profile = buf.readbyte()
        self.profile_compatibility = buf.readbyte()
        self.level = buf.readbyte()
        buf.readbits(6)
        self.len_minus_1 = buf.readbits(2)
        buf.readbits(3)

        self.sps = []
        num_of_sps = buf.readbits(5)
        for _ in range(num_of_sps):
            sps_len = buf.readint16()
            self.sps.append(buf.readbytes(sps_len))

        self.pps = []
        num_of_pps = buf.readbyte()
        for _ in range(num_of_pps):
            pps_len = buf.readint16()
            self.pps.append(buf.readbytes(pps_len))

        if self.remaining_bytes() >= 4:
            buf.readbits(6)
            self.chroma_format = buf.readbits(2)
            buf.readbits(5)
            self.bit_depth_luma_minus_8 = buf.readbits(3)
            buf.readbits(5)
            self.bit_depth_chroma_minus_8 = buf.readbits(3)
            self.sps_ext_len = buf.readbyte()
            buf.skipbytes(self.sps_ext_len)
        else:
            self.chroma_format = -1

        self.has_children = False

    def generate_fields(self):
        super().generate_fields()
        yield ("Confiuration level", self.configuration_level)
        yield ("Profile", self.profile)
        yield ("Profile compatibility", self.profile_compatibility)
        yield ("Level", self.level)
        yield ("Length size minus 1", self.len_minus_1)
        yield ("number of sps", len(self.sps))
        for sps in self.sps:
            yield ("SPS", sps)
        yield ("number of pps", len(self.pps))
        for pps in self.pps:
            yield ("PPS", pps)
        if self.chroma_format != -1:
            yield ("chroma format", self.chroma_format)
            yield ("bit depth luma minus 8", self.bit_depth_luma_minus_8)
            yield ("bit depth chroma minus 8", self.bit_depth_chroma_minus_8)
            yield ("sps ext byte count", self.sps_ext_len)


boxmap = {
    "mvhd": MovieHeader,
    "tkhd": TrackHeader,
    "mdhd": MediaHeader,
    "vmhd": VideoMediaHeader,
    "smhd": SoundMediaHeader,
    "hmhd": HintMediaHeader,
    "hdlr": HandlerBox,
    "stsd": SampleDescription,
    "dref": DataReferenceBox,
    "stts": TimeToSampleBox,
    "stsc": SampleToChunkBox,
    "stco": ChunkOffsetBox,
    "stss": SyncSampleBox,
    "stsz": SampleSizeBox,
    "stz2": CompactSampleSizeBox,
    "url ": DataEntryUrlBox,
    "urn ": DataEntryUrnBox,
    "mehd": MovieExtendsHeader,
    "trex": TrackExtendsBox,
    "avcC": AvcCBox,
}
