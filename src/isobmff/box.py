
import sys


class Box(object):
    def __init__(self, buf, parent=None, container = False):
        self.parent = parent
        self.parse(buf, container)

    def parse(self, buf, container = False):
        islarge = False
        size = buf.readint32()
        boxtype = buf.readstr(4)
        self.consumed_bytes = 8
        # 64 bit box
        if size == 1:
            size = buf.readint64()
            self.consumed_bytes += 8
            islarge = True

        self.size = size
        self.boxtype = boxtype
        self.islarge = islarge
        self.children = []
        # usertype
        if boxtype == 'uuid':
            buf.skipbytes(16)
            self.consumed_bytes += 16

        if container:
            self.parse_children(buf)

    def parse_children(self, buf):
        while self.consumed_bytes < self.size:
            box = getnextbox(buf, self)
            self.children.append(box)
            self.consumed_bytes += box.size

    def display(self, fmt_info, my_index=0):
        fmt_info.update(len(self.children) != 0)
        sys.stdout.write("%s" %(self.formatted_str(fmt_info)))
        nxt_fmt = fmt_info.get_next(True)
        for i in range(self.get_child_count()):
            if i + 1 == self.get_child_count():
                nxt_fmt.set_siblingstatus(False)
            self.children[i].display(nxt_fmt, i)

    def formatted_str(self, fmt_info):
        s = fmt_info.add_header(self.boxtype)
        return s + fmt_info.add_attr("size", self.size)

    def get_child_count(self):
        return len(self.children)

    def find_parent(self, boxtype):
        p = self.parent
        while p is not None:
            if p.boxtype == boxtype:
                return p
            p = p.parent

    def find_child(self, boxtype):
        for child in self.children:
            if child.boxtype == boxtype:
                return child

    def __str__(self):
        return "%s:%d" %(self.boxtype, self.size)


class FullBox(Box):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

    def parse(self, buf):
        super(FullBox, self).parse(buf)
        self.version = buf.readbyte()
        self.flags = buf.readint(3)
        self.consumed_bytes += 4

    def formatted_str(self, fmt_info):
        s = super(FullBox, self).formatted_str(fmt_info)
        s += fmt_info.add_data("version: %s" %(self.version))
        return s + fmt_info.add_data("flags: 0x%06X" %(self.flags))


class FileType(Box):
    def __init__(self, buf, parent=None):
        self.parent = parent
        self.parse(buf)

    def parse(self, buf):
        super(FileType, self).parse(buf)
        self.major_brand = buf.readstr(4)
        self.minor_version = buf.readint32()
        self.consumed_bytes += 8
        self.brands = []
        while self.consumed_bytes < self.size:
            self.brands.append(buf.readstr(4))
            self.consumed_bytes += 4

    def formatted_str(self, fmt_info):
        s = super(FileType, self).formatted_str(fmt_info)
        s += fmt_info.add_data("major brand: %s" %(self.major_brand))
        s += fmt_info.add_data("minor version: %d" %(self.minor_version))
        return s + fmt_info.add_data("brands: %s" %(','.join(self.brands)))

    def __str__(self):
        return super(FileType, self).__str__() + " %s %d with %d brands %s" %(
                self.major_brand, self.minor_version, len(self.brands), ','.join(self.brands)
            )


class MovieHeader(FullBox):
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
        s = super(MovieHeader, self).formatted_str(fmt_info)
        s += fmt_info.add_data("creation time: %d" %(self.creation_time))
        s += fmt_info.add_data("modification time: %d" %(self.modification_time))
        s += fmt_info.add_data("timescale: %d" %(self.timescale))
        s += fmt_info.add_data("duration: %d" %(self.duration))
        s += fmt_info.add_data("rate: 0x%08X" %(self.rate))
        s += fmt_info.add_data("volume: 0x%04X" %(self.volume))
        s += fmt_info.add_data("matrix:")
        for i in range(3):
            s += fmt_info.add_data('  ' + ', '.join(["0x%08X" %(k) for k in self.matrix[i]]))
        s += fmt_info.add_data("next track id: %d" %(self.next_track_id))
        return s


class TrackHeader(FullBox):
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
        s = super(TrackHeader, self).formatted_str(fmt_info)
        s += fmt_info.add_data("creation time: %d" %(self.creation_time))
        s += fmt_info.add_data("modification time: %d" %(self.modification_time))
        s += fmt_info.add_data("track id: %d" %(self.track_id))
        s += fmt_info.add_data("duration: %d" %(self.duration))
        s += fmt_info.add_data("layer: 0x%04X" %(self.layer))
        s += fmt_info.add_data("alternate group: 0x%04X" %(self.altgroup))
        s += fmt_info.add_data("volume: 0x%04X" %(self.volume))
        s += fmt_info.add_data("matrix:")
        for i in range(3):
            s += fmt_info.add_data('  ' + ', '.join(["0x%08X" %(k) for k in self.matrix[i]]))
        s += fmt_info.add_data("width: %d" %(self.width))
        s += fmt_info.add_data("height: %d" %(self.height))
        return s


class MediaHeader(FullBox):
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
        s = super(MediaHeader, self).formatted_str(fmt_info)
        s += fmt_info.add_data("creation time: %d" %(self.creation_time))
        s += fmt_info.add_data("modification time: %d" %(self.modification_time))
        s += fmt_info.add_data("timescale: %d" %(self.timescale))
        s += fmt_info.add_data("duration: %d" %(self.duration))
        s += fmt_info.add_data("language: %d (%s)" %(self.language, parse_iso639_2_15bit(self.language)))
        return s


class HandlerBox(FullBox):
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
        s += fmt_info.add_data("handler: %s" %(self.handler))
        s += fmt_info.add_data("name: %s" %(self.name if len(self.name) else '<empty>'))
        return s


class SampleEntry(Box):
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
        s += fmt_info.add_data("data reference index: %d" %(self.data_ref_index))
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
        s += fmt_info.add_data("width: %d" %(self.width))
        s += fmt_info.add_data("height: %d" %(self.height))
        s += fmt_info.add_data("horizontal resolution: 0x%08X" %(self.hori_resolution))
        s += fmt_info.add_data("vertical resolution: 0x%08X" %(self.vert_resolution))
        s += fmt_info.add_data("frame count: %d" %(self.frame_count))
        s += fmt_info.add_data("compressor name: %s" %(self.compressor_name))
        s += fmt_info.add_data("depth: %d" %(self.depth))
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
        s += fmt_info.add_data("channel count: %d" %(self.channel_count))
        s += fmt_info.add_data("sample size: %d" %(self.sample_size))
        s += fmt_info.add_data("sample rate: 0x%02X (%d, %d)" %(
            self.sample_rate, self.sample_rate >> 16, self.sample_rate & 0xFFFF
        ))
        return s


class SampleDescription(FullBox):
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
                entry = Box(buf)
                buf.skipbytes(entry.size - entry.consumed_bytes)
            self.entries.append(entry)

    def display(self, fmt_info, my_index=0):
        fmt_info.update(self.entry_count != 0)
        sys.stdout.write("%s" %(self.formatted_str(fmt_info)))

    def formatted_str(self, fmt_info):
        s = super(SampleDescription, self).formatted_str(fmt_info)
        s += fmt_info.add_data("entry count: %d" %(self.entry_count))
        nxt_fmt = fmt_info.get_next()
        for i in range(len(self.entries)):
            if i + 1 == len(self.entries):
                nxt_fmt.set_siblingstatus(False)
            s += self.entries[i].formatted_str(nxt_fmt)
        return s


def getnextbox(buf, parent=None):
    fourcc = buf.peekstr(4, 4)
    if fourcc == 'ftyp':
        box = FileType(buf, parent)
    elif fourcc == 'mvhd':
        box = MovieHeader(buf, parent)
    elif fourcc == 'tkhd':
        box = TrackHeader(buf, parent)
    elif fourcc == 'mdhd':
        box = MediaHeader(buf, parent)
    elif fourcc == 'hdlr':
        box = HandlerBox(buf, parent)
    elif fourcc == 'stsd':
        box = SampleDescription(buf, parent)
    elif fourcc in ['moov', 'trak', 'edts', 'mdia',
            'minf', 'dinf', 'stbl', 'mvex',
            'moof', 'traf', 'mfra', 'skip',
            'meta', 'ipro', 'sinf']:
        box = Box(buf, parent, True)
    else:
        box = Box(buf, parent)
        #TODO: Handle size zero (box extends till EOF).
        buf.skipbytes(box.size - box.consumed_bytes)
    return box


def getboxlist(buf, parent=None):
    boxes = []
    try:
        while buf.hasmore():
            box = getnextbox(buf, parent)
            boxes.append(box)
    except:
        import traceback
        print traceback.format_exc()

    return boxes

