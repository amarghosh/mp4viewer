
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
            box = Box.getnextbox(buf, self)
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


    @staticmethod
    def getnextbox(buf, parent=None):
        from movie import *
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
            box = Box.getnextbox(buf, parent)
            boxes.append(box)
    except:
        import traceback
        print traceback.format_exc()
    return boxes


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
        s += fmt_info.add_attr("version", self.version)
        return s + fmt_info.add_attr("flags", "0x%06X" %(self.flags))


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
        s += fmt_info.add_attr("major brand", self.major_brand)
        s += fmt_info.add_attr("minor version", self.minor_version)
        return s + fmt_info.add_attr("brands", ','.join(self.brands))

    def __str__(self):
        return super(FileType, self).__str__() + " %s %d with %d brands %s" %(
                self.major_brand, self.minor_version, len(self.brands), ','.join(self.brands)
            )

