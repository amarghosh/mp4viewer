
class Box(object):
    def __init__(self, buf, container = False):
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
        self.children = getboxlist(buf, self.size - self.consumed_bytes)

    def display(self, prefix=''):
        print "%s" %(self.formatted_str(prefix))
        for child in self.children:
            child.display(prefix + '    ')

    def formatted_str(self, prefix):
        import re
        s = re.sub('    $', '`---', prefix) + self.boxtype + ':\n'
        prefix += '    '
        s += prefix + "size: %d" %(self.size)
        return s

    def __str__(self):
        return "%s:%d" %(self.boxtype, self.size)


class FullBox(Box):
    def __init__(self, buf):
        self.parse(buf)

    def parse(self, buf):
        super(FullBox, self).parse(buf)
        self.version = buf.readbyte()
        self.flags = buf.readint(3)
        self.consumed_bytes += 4

    def formatted_str(self, prefix):
        s = super(FullBox, self).formatted_str(prefix) + '\n'
        prefix += '    '
        s += prefix + "version: %s" %(self.version) + "\n"
        s += prefix + "flags: 0x%06X" %(self.flags)
        return s


class FileType(Box):
    def __init__(self, buf):
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

    def formatted_str(self, prefix):
        s = super(FileType, self).formatted_str(prefix) + '\n'
        prefix += '    '
        s += prefix + "major brand: %s" %(self.major_brand) + "\n"
        s += prefix + "minor version: %d" %(self.minor_version) + "\n"
        s += prefix + "brands: %s" %(','.join(self.brands))
        return s

    def __str__(self):
        return super(FileType, self).__str__() + " %s %d with %d brands %s" %(
                self.major_brand, self.minor_version, len(self.brands), ','.join(self.brands)
            )


class MovieHeader(FullBox):
    def __init__(self, buf):
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

    def formatted_str(self, prefix):
        s = super(MovieHeader, self).formatted_str(prefix) + '\n'
        prefix += '    '
        s += prefix + "creation time: %d" %(self.creation_time) + "\n"
        s += prefix + "modification time: %d" %(self.modification_time) + "\n"
        s += prefix + "timescale: %d" %(self.timescale) + "\n"
        s += prefix + "duration: %d" %(self.duration) + "\n"
        s += prefix + "rate: 0x%08X" %(self.rate) + "\n"
        s += prefix + "volume: 0x%04X" %(self.volume) + "\n"
        s += prefix + "matrix:" + '\n'
        for i in range(3):
            s += prefix + '  ' + ', '.join(["0x%08X" %(k) for k in self.matrix[i]]) + '\n'
        s += prefix + "next track id: %d" %(self.next_track_id)
        return s


class TrackHeader(FullBox):
    def __init__(self, buf):
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

    def formatted_str(self, prefix):
        s = super(TrackHeader, self).formatted_str(prefix) + '\n'
        prefix += '    '
        s += prefix + "creation time: %d" %(self.creation_time) + "\n"
        s += prefix + "modification time: %d" %(self.modification_time) + "\n"
        s += prefix + "track id: %d" %(self.track_id) + "\n"
        s += prefix + "duration: %d" %(self.duration) + "\n"
        s += prefix + "layer: 0x%04X" %(self.layer) + "\n"
        s += prefix + "alternate group: 0x%04X" %(self.altgroup) + "\n"
        s += prefix + "volume: 0x%04X" %(self.volume) + "\n"
        s += prefix + "matrix:" + '\n'
        for i in range(3):
            s += prefix + '  ' + ', '.join(["0x%08X" %(k) for k in self.matrix[i]]) + '\n'
        s += prefix + "width: %d" %(self.width) + '\n'
        s += prefix + "height: %d" %(self.height)
        return s


class MediaHeader(FullBox):
    def __init__(self, buf):
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

    def formatted_str(self, prefix):
        from utils import parse_iso639_2_15bit
        s = super(MediaHeader, self).formatted_str(prefix) + '\n'
        prefix += '    '
        s += prefix + "creation time: %d" %(self.creation_time) + "\n"
        s += prefix + "modification time: %d" %(self.modification_time) + "\n"
        s += prefix + "timescale: %d" %(self.timescale) + "\n"
        s += prefix + "duration: %d" %(self.duration) + "\n"
        s += prefix + "language: %d (%s)" %(self.language, parse_iso639_2_15bit(self.language))
        return s


def getboxlist(buf, maxlength=-1):
    boxes = []
    bytes_consumed = 0
    while buf.hasmore():
        if maxlength != -1 and bytes_consumed >= maxlength:
            break
        fourcc = buf.peekstr(4, 4)
        if fourcc == 'ftyp':
            box = FileType(buf)
        elif fourcc == 'mvhd':
            box = MovieHeader(buf)
        elif fourcc == 'tkhd':
            box = TrackHeader(buf)
        elif fourcc == 'mdhd':
            box = MediaHeader(buf)
        elif fourcc in ['moov', 'trak', 'edts', 'mdia',
                'minf', 'dinf', 'stbl', 'mvex',
                'moof', 'traf', 'mfra', 'skip',
                'meta', 'ipro', 'sinf']:
            box = Box(buf, True)
        else:
            box = Box(buf)
            #TODO: Handle size zero (box extends till EOF).
            buf.skipbytes(box.size - box.consumed_bytes)
        boxes.append(box)
        # size zero
        bytes_consumed += box.size

    return boxes


