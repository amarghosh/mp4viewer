
import sys
import box

class MovieHeader(box.FullBox):
    def parse(self, buf):
        super(MovieHeader, self).parse(buf)
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
        self.matrix = []
        for i in range(3):
            self.matrix.append([buf.readint32() for j in range(3)])
        buf.skipbytes(24)
        self.next_track_id = buf.readint32()

    def generate_fields(self):
        for x in super(MovieHeader, self).generate_fields():
            yield x
        from utils import get_utc_from_seconds_since_1904
        yield ("creation time", self.creation_time, get_utc_from_seconds_since_1904(self.creation_time).ctime())
        yield ("modification time", self.creation_time, get_utc_from_seconds_since_1904(self.modification_time).ctime())
        yield ("timescale", self.timescale)
        yield ("duration", self.duration)
        yield ("rate", "0x%08X" %(self.rate))
        yield ("volume", "0x%04X" %(self.volume))
        yield ("matrix", self.matrix)
        yield ("next track id", self.next_track_id)


class TrackHeader(box.FullBox):
    def parse(self, buf):
        super(TrackHeader, self).parse(buf)
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
        self.matrix = []
        for i in range(3):
            self.matrix.append([buf.readint32() for j in range(3)])
        self.width = buf.readint32()
        self.height = buf.readint32()

    def generate_fields(self):
        for x in super(TrackHeader, self).generate_fields():
            yield x
        from utils import get_utc_from_seconds_since_1904
        yield ("creation time", self.creation_time, get_utc_from_seconds_since_1904(self.creation_time).ctime())
        yield ("modification time", self.modification_time, get_utc_from_seconds_since_1904(self.modification_time).ctime())
        yield ("track id", self.track_id)
        yield ("duration", self.duration)
        yield ("layer", "0x%04X" %(self.layer))
        yield ("alternate group", "0x%04X" %(self.altgroup))
        yield ("volume", "0x%04X" %(self.volume))
        yield ("matrix", self.matrix)
        yield ("width", self.width)
        yield ("height", self.height)


class MediaHeader(box.FullBox):
    def parse(self, buf):
        super(MediaHeader, self).parse(buf)
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
        from utils import parse_iso639_2_15bit
        from utils import get_utc_from_seconds_since_1904
        for x in super(MediaHeader, self).generate_fields():
            yield x
        yield ("creation time", self.creation_time, get_utc_from_seconds_since_1904(self.creation_time).ctime())
        yield ("modification time", self.modification_time, get_utc_from_seconds_since_1904(self.modification_time).ctime())
        yield ("timescale", self.timescale)
        yield ("duration", self.duration)
        yield ("language", self.language, parse_iso639_2_15bit(self.language))


class HandlerBox(box.FullBox):
    def parse(self, buf):
        super(HandlerBox, self).parse(buf)
        buf.skipbytes(4)
        self.handler = buf.readstr(4)
        buf.skipbytes(12)
        self.consumed_bytes += 20
        self.name = buf.read_cstring(self.size - self.consumed_bytes)[0]

    def generate_fields(self):
        for x in super(HandlerBox, self).generate_fields():
            yield x
        yield ("handler", self.handler)
        yield ("name", self.name if len(self.name) else '<empty>')


class SampleEntry(box.Box):
    def parse(self, buf):
        super(SampleEntry, self).parse(buf)
        buf.skipbytes(6)
        self.data_ref_index = buf.readint16()
        self.consumed_bytes += 8

    def generate_fields(self):
        for x in super(SampleEntry, self).generate_fields():
            yield x
        yield ("data reference index", self.data_ref_index)


class HintSampleEntry(SampleEntry):
    def parse(self, buf):
        buf.skipbytes(self.size - self.consumed_bytes)


class VisualSampleEntry(SampleEntry):
    def parse(self, buf):
        super(VisualSampleEntry, self).parse(buf)
        buf.skipbytes(2 + 2 + 3 * 4)
        self.width = buf.readint16()
        self.height = buf.readint16()
        self.hori_resolution = buf.readint32()
        self.vert_resolution = buf.readint32()
        buf.skipbytes(4)
        self.frame_count = buf.readint16()
        compressor_name_length = buf.readbyte()
        self.compressor_name = buf.readstr(compressor_name_length) if compressor_name_length else ''
        buf.skipbytes(32 - compressor_name_length - 1)
        self.depth = buf.readint16()
        buf.skipbytes(2)

    def generate_fields(self):
        for x in super(VisualSampleEntry, self).generate_fields():
            yield x
        yield ("width", self.width)
        yield ("height", self.height)
        yield ("horizontal resolution", "0x%08X" %(self.hori_resolution))
        yield ("vertical resolution", "0x%08X" %(self.vert_resolution))
        yield ("frame count", self.frame_count)
        yield ("compressor name", self.compressor_name)
        yield ("depth", self.depth)

class AudioSampleEntry(SampleEntry):
    def parse(self, buf):
        super(AudioSampleEntry, self).parse(buf)
        buf.skipbytes(8)
        self.channel_count = buf.readint16()
        self.sample_size = buf.readint16()
        buf.skipbytes(4)
        self.sample_rate = buf.readint32()

    def generate_fields(self):
        for x in super(AudioSampleEntry, self).generate_fields():
            yield x
        yield ("sample size", self.sample_size)
        yield ("sample rate", self.sample_rate, "%d, %d" %(self.sample_rate >> 16, self.sample_rate & 0xFFFF))


class SampleDescription(box.FullBox):
    def parse(self, buf):
        super(SampleDescription, self).parse(buf)
        media = self.find_parent('mdia')
        hdlr = media.find_child('hdlr') if media else None
        handler = hdlr.handler if hdlr else None
        self.entry_count = buf.readint32()
        self.entries = []
        for i in range(self.entry_count):
            if handler == 'soun':
                entry = AudioSampleEntry(buf)
            elif handler == 'vide':
                entry = VisualSampleEntry(buf)
            elif handler == 'hint':
                entry = HintSampleEntry(buf)
            else:
                entry = box.Box(buf)
                buf.skipbytes(entry.size - entry.consumed_bytes)
            self.entries.append(entry)

    def generate_fields(self):
        for x in super(SampleDescription, self).generate_fields():
            yield x
        yield ("entry count", self.entry_count)
        for entry in self.entries:
            yield entry


class DataEntryUrnBox(box.FullBox):
    def parse(self, buf):
        super(DataEntryUrnBox, self).parse(buf)
        self.name = buf.read_cstring()[0]
        self.location = buf.read_cstring()[0]

    def generate_fields(self):
        for x in super(DataEntryUrnBox, self).generate_fields():
            yield x
        yield ("name", self.name)
        yield ("location", self.location)


class DataEntryUrlBox(box.FullBox):
    def parse(self, buf):
        super(DataEntryUrlBox, self).parse(buf)
        self.location = buf.read_cstring(self.size - self.consumed_bytes)[0]

    def generate_fields(self):
        for x in super(DataEntryUrlBox, self).generate_fields():
            yield x
        yield ("location", self.location)


class DataReferenceBox(box.FullBox):
    def parse(self, buf):
        super(DataReferenceBox, self).parse(buf)
        self.entry_count = buf.readint32()
        self.entries = []
        for i in range(self.entry_count):
            entry_name = buf.peekstr(4, 4)
            if entry_name == 'url ':
                self.entries.append(DataEntryUrlBox(buf, self))
            elif entry_name == 'urn ':
                self.entries.append(DataEntryUrnBox(buf, self))
            else:
                self.entries.append(box.Box.getnextbox(buf, self))

    def generate_fields(self):
        for x in super(DataReferenceBox, self).generate_fields():
            yield x
        yield ("entry count", self.entry_count)
        for entry in self.entries:
            yield entry


class TimeToSampleBox(box.FullBox):
    def parse(self, buf):
        super(TimeToSampleBox, self).parse(buf)
        self.entry_count = buf.readint32()
        self.entries = []
        for i in range(self.entry_count):
            count = buf.readint32()
            delta = buf.readint32()
            self.entries.append((count, delta))

    def generate_fields(self):
        for x in super(TimeToSampleBox, self).generate_fields():
            yield x
        yield ("entry count", self.entry_count)
        for entry in self.entries:
            yield ("sample count", entry[0])
            yield ("sample delta", entry[1])


class SampleToChunkBox(box.FullBox):
    def parse(self, buf):
        super(SampleToChunkBox, self).parse(buf)
        self.entry_count = buf.readint32()
        self.entries = []
        for i in range(self.entry_count):
            first = buf.readint32()
            samples_per_chunk = buf.readint32()
            sdix = buf.readint32()
            self.entries.append((first, samples_per_chunk, sdix))

    def generate_fields(self):
        for x in super(SampleToChunkBox, self).generate_fields():
            yield x
        yield ("entry count", self.entry_count)
        for entry in self.entries:
            yield ("first chunk", entry[0])
            yield ("samples per chunk", entry[1])
            yield ("sample description index", entry[2])


class ChunkOffsetBox(box.FullBox):
    def parse(self, buf):
        super(ChunkOffsetBox, self).parse(buf)
        self.entry_count = buf.readint32()
        self.entries = []
        for i in range(self.entry_count):
            self.entries.append(buf.readint32())

    def generate_fields(self):
        for x in super(ChunkOffsetBox, self).generate_fields():
            yield x
        yield ("entry count", self.entry_count)
        yield ("chunk offsets", self.entries)


class SyncSampleBox(box.FullBox):
    def parse(self, buf):
        super(SyncSampleBox, self).parse(buf)
        self.entry_count = buf.readint32()
        self.entries = []
        for i in range(self.entry_count):
            self.entries.append(buf.readint32())

    def generate_fields(self):
        for x in super(SyncSampleBox, self).generate_fields():
            yield x
        yield ("entry count", self.entry_count)
        yield ("sample numbers", self.entries)


class SampleSizeBox(box.FullBox):
    def parse(self, buf):
        super(SampleSizeBox, self).parse(buf)
        self.sample_size = buf.readint32()
        self.sample_count = buf.readint32()
        self.entries = []
        if self.sample_size == 0:
            for i in range(self.sample_count):
                self.entries.append(buf.readint32())

    def generate_fields(self):
        for x in super(SampleSizeBox, self).generate_fields():
            yield x
        yield ("sample size", self.sample_size)
        yield ("sample count", self.sample_count)
        if self.sample_size == 0:
            yield ("sample sizes", self.entries)


class CompactSampleSizeBox(box.FullBox):
    def parse(self, buf):
        super(CompactSampleSizeBox, self).parse(buf)
        buf.skipbytes(3)
        self.field_size = buf.readbyte()
        self.sample_count = buf.readint32()
        self.entries = [buf.readbits(self.field_size) for i in range(self.sample_count)]
        # skip padding bits
        if self.field_size == 4 and self.sample_count % 2 != 0:
            buf.readbits(4)

    def generate_fields(self):
        for x in super(SampleSizeBox, self).generate_fields():
            yield x
        yield ("field size", self.sample_size)
        yield ("sample count", self.sample_count)
        yield ("entries", self.entries)
