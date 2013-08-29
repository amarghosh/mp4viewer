
import sys
import box

class MovieHeader(box.FullBox):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

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

    def formatted_str(self, fmt_info):
        from utils import utc_from_seconds_since_1904
        s = super(MovieHeader, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("creation time", "%s (%d)" %(
            utc_from_seconds_since_1904(self.creation_time).ctime(), self.creation_time))
        s += fmt_info.add_attr("modification time", "%s (%d)" %(
            utc_from_seconds_since_1904(self.modification_time).ctime(), self.modification_time))
        s += fmt_info.add_attr("timescale", self.timescale)
        s += fmt_info.add_attr("duration", self.duration)
        s += fmt_info.add_attr("rate", "0x%08X" %(self.rate))
        s += fmt_info.add_attr("volume", "0x%04X" %(self.volume))
        s += fmt_info.add_attr("matrix", '')
        for i in range(3):
            s += fmt_info.add_data('  ' + ', '.join(["0x%08X" %(k) for k in self.matrix[i]]))
        s += fmt_info.add_attr("next track id", self.next_track_id)
        return s


class TrackHeader(box.FullBox):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

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

    def formatted_str(self, fmt_info):
        from utils import utc_from_seconds_since_1904
        s = super(TrackHeader, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("creation time", "%s (%d)" %(
            utc_from_seconds_since_1904(self.creation_time).ctime(), self.creation_time))
        s += fmt_info.add_attr("modification time", "%s (%d)" %(
            utc_from_seconds_since_1904(self.modification_time).ctime(), self.modification_time))
        s += fmt_info.add_attr("track id", self.track_id)
        s += fmt_info.add_attr("duration", self.duration)
        s += fmt_info.add_attr("layer", "0x%04X" %(self.layer))
        s += fmt_info.add_attr("alternate group", "0x%04X" %(self.altgroup))
        s += fmt_info.add_attr("volume", "0x%04X" %(self.volume))
        s += fmt_info.add_attr("matrix", '')
        for i in range(3):
            s += fmt_info.add_data('  ' + ', '.join(["0x%08X" %(k) for k in self.matrix[i]]))
        s += fmt_info.add_attr("width", self.width)
        s += fmt_info.add_attr("height", self.height)
        return s


class MediaHeader(box.FullBox):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

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

    def formatted_str(self, fmt_info):
        from utils import parse_iso639_2_15bit
        from utils import utc_from_seconds_since_1904
        s = super(MediaHeader, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("creation time", "%s (%d)" %(
            utc_from_seconds_since_1904(self.creation_time).ctime(), self.creation_time))
        s += fmt_info.add_attr("modification time", "%s (%d)" %(
            utc_from_seconds_since_1904(self.modification_time).ctime(), self.modification_time))
        s += fmt_info.add_attr("timescale", self.timescale)
        s += fmt_info.add_attr("duration", self.duration)
        s += fmt_info.add_attr("language", "%d (%s)" %(self.language, parse_iso639_2_15bit(self.language)))
        return s


class HandlerBox(box.FullBox):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

    def parse(self, buf):
        super(HandlerBox, self).parse(buf)
        buf.skipbytes(4)
        self.handler = buf.readstr(4)
        buf.skipbytes(12)
        self.consumed_bytes += 20
        remaining = self.size - self.consumed_bytes
        name = ''
        for i in range(remaining):
            c = buf.readbyte()
            if not c:
                break
            name += c
        self.name = name

    def formatted_str(self, fmt_info):
        s = super(HandlerBox, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("handler", self.handler)
        s += fmt_info.add_attr("name", self.name if len(self.name) else '<empty>')
        return s


class SampleEntry(box.Box):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

    def parse(self, buf):
        super(SampleEntry, self).parse(buf)
        buf.skipbytes(6)
        self.data_ref_index = buf.readint16()
        self.consumed_bytes += 8

    def formatted_str(self, fmt_info):
        s = super(SampleEntry, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("data reference index", self.data_ref_index)
        return s


class HintSampleEntry(SampleEntry):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)
        buf.skipbytes(self.size - self.consumed_bytes)


class VisualSampleEntry(SampleEntry):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

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

    def formatted_str(self, fmt_info):
        s = super(VisualSampleEntry, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("width", self.width)
        s += fmt_info.add_attr("height", self.height)
        s += fmt_info.add_attr("horizontal resolution", "0x%08X" %(self.hori_resolution))
        s += fmt_info.add_attr("vertical resolution", "0x%08X" %(self.vert_resolution))
        s += fmt_info.add_attr("frame count", self.frame_count)
        s += fmt_info.add_attr("compressor name", self.compressor_name)
        s += fmt_info.add_attr("depth", self.depth)
        return s

class AudioSampleEntry(SampleEntry):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

    def parse(self, buf):
        super(AudioSampleEntry, self).parse(buf)
        buf.skipbytes(8)
        self.channel_count = buf.readint16()
        self.sample_size = buf.readint16()
        buf.skipbytes(4)
        self.sample_rate = buf.readint32()

    def formatted_str(self, fmt_info):
        s = super(AudioSampleEntry, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("channel count", self.channel_count)
        s += fmt_info.add_attr("sample size", self.sample_size)
        s += fmt_info.add_attr("sample rate", "0x%02X (%d, %d)" %(self.sample_rate,
            self.sample_rate >> 16, self.sample_rate & 0xFFFF))
        return s


class SampleDescription(box.FullBox):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

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

    def display(self, fmt_info, my_index=0):
        fmt_info.update(self.entry_count != 0)
        sys.stdout.write("%s" %(self.formatted_str(fmt_info)))

    def formatted_str(self, fmt_info):
        s = super(SampleDescription, self).formatted_str(fmt_info)
        s += fmt_info.add_attr("entry count", self.entry_count)
        nxt_fmt = fmt_info.get_next()
        for i in range(len(self.entries)):
            if i + 1 == len(self.entries):
                nxt_fmt.set_siblingstatus(False)
            s += self.entries[i].formatted_str(nxt_fmt)
        return s

