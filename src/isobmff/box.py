
import sys

# Set container flag for pure containers. Boxes with data and children should be
# handled in their own subclass
class Box(object):
    box_names = {
        #iso bmff box types
        'ftyp' : 'File type',
        'moov' : 'Movie container',
        'moof' : 'Movie fragment',
        'mfra' : 'Movie fragment random access',
        'mfhd' : 'Movie fragment header',
        'traf' : 'Track fragment',
        'tfhd' : 'Track fragment header',
        'trun' : 'Track fragment run',
        'saiz' : 'Sample auxiliary information sizes',
        'saio' : 'Sample auxiliary information offsets',
        'tfdt' : 'Track fragment decode time',
        'trak' : 'Track container',
        'mdia' : 'Media container',
        'minf' : 'Media information box',
        'dinf' : 'Data information box',
        'vmhd' : 'Video media header',
        'smhd' : 'Sound media header',
        'hmhd' : 'hint media header',
        'mvhd' : 'Movie header',
        'tkhd' : 'Track header',
        'mdhd' : 'Media header',
        'stbl' : 'Sample table',
        'hdlr' : 'Handler box',
        'stsd' : 'Sample description',
        'dref' : 'Data reference box',
        'url ' : 'Data entry URL box',
        'stts' : 'Time-to-sample box',
        'stsc' : 'Sample-to-chunk box',
        'stco' : 'Chunk offset box',
        'stss' : 'Sync sample box',
        'stsz' : 'Sample size box',
        'stz2' : 'Compact sample size box',
        'mvex' : 'Movie extends box',
        'mehd' : 'Movie extends header box',
        'trex' : 'Track extends defaults',
        'udta' : 'User data',
        'skip' : 'Skip',
        'free' : 'Free',
        'mdat' : 'Media data container',
        'styp' : 'Segment type',
        'sidx' : 'Segment index',
        'ssix' : 'Subsegment index',
        'sbgp' : 'Sample to group box',
        'sgpd' : 'Sample group description box',
        #common encryption boxes
        'tenc' : 'Track encryption box',
        'senc' : 'Sample encryption box',
        'pssh' : 'Protection system specific header box',
        'schm' : 'Scheme type box',
        'schi' : 'Scheme information box',
        'sinf' : 'Protection scheme information box',
        'frma' : 'Original format box',
        #flv specific boxes
        'afra' : 'Adobe fragment random access box',
        'abst' : 'Adobe bootstrap info box',
        'asrt' : 'Adobe segment run table box',
        'afrt' : 'Adobe fragment run table box',
    }
    container_boxes = [
        'moov', 'trak', 'edts', 'mdia', 'minf', 'dinf', 'stbl', 'mvex',
        'moof', 'traf', 'mfra', 'skip', 'meta', 'ipro', 'sinf', 'schi',
    ]

    def __init__(self, buf, parent=None, is_container = False):
        self.parent = parent
        pos = buf.current_position()
        self.has_children = is_container
        # has_children can be updated by parse() of the derived class
        self.parse(buf)
        self.consumed_bytes = buf.current_position() - pos
        if self.has_children:
            self.parse_children(buf)

    def parse(self, buf):
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

    def parse_children(self, buf):
        while self.consumed_bytes < self.size:
            box = Box.getnextbox(buf, self)
            self.children.append(box)
            self.consumed_bytes += box.size

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

    def generate_fields(self):
        yield ("size", self.size)

    def __str__(self):
        return "%s (%d bytes)" %(self.boxtype, self.size)

    @staticmethod
    def getnextbox(buf, parent=None):
        import movie
        import fragment
        import flv
        import cenc
        boxmap = {
            'ftyp' : FileType,
        }
        boxmap.update(movie.boxmap)
        boxmap.update(fragment.boxmap)
        boxmap.update(flv.boxmap)
        boxmap.update(cenc.boxmap)
        fourcc = buf.peekstr(4, 4)
        if fourcc in boxmap:
            box = boxmap[fourcc](buf, parent)
        else:
            container = fourcc in Box.container_boxes
            box = Box(buf, parent, container)
            if not container:
                #TODO: Handle size zero (box extends till EOF).
                buf.skipbytes(box.size - box.consumed_bytes)
        return box

    @staticmethod
    def getboxdesc(name):
        if name in Box.box_names:
            return Box.box_names[name]
        else:
            return name.upper()


class FullBox(Box):
    def parse(self, buf):
        super(FullBox, self).parse(buf)
        self.version = buf.readbyte()
        self.flags = buf.readint(3)
        self.consumed_bytes += 4

    def generate_fields(self):
        for x in super(FullBox, self).generate_fields():
            yield x
        yield ("version", self.version)
        yield ("flags", "0x%06X" %self.flags)


class FileType(Box):
    def parse(self, buf):
        super(FileType, self).parse(buf)
        self.major_brand = buf.readstr(4)
        self.minor_version = buf.readint32()
        self.consumed_bytes += 8
        self.brands = []
        while self.consumed_bytes < self.size:
            self.brands.append(buf.readstr(4))
            self.consumed_bytes += 4

    def generate_fields(self):
        super(FileType, self).generate_fields()
        yield ("major brand", self.major_brand)
        yield ("minor version", self.minor_version)
        yield ("brands", ','.join(self.brands))

    def __str__(self):
        return super(FileType, self).__str__() + " %s %d with %d brands %s" %(
                self.major_brand, self.minor_version, len(self.brands), ','.join(self.brands)
            )

