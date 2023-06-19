from __future__ import print_function
from __future__ import absolute_import

import traceback

import sys

def string_to_hex(s):
    x = [ "%02x" %ord(ch) for ch in s]
    return " ".join(x)

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
        'elst' : 'Edit list',
        'colr' : 'Colour information',
        'ctts' : 'Composition offset',
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

    # Avoid printing parsing errors for known data boxes
    data_boxes = ['mdat', 'udta']

    def __init__(self, buf, parent=None, is_container = False):
        self.parent = parent
        pos = buf.current_position()
        self.buffer_offset = pos
        self.has_children = is_container
        # has_children can be updated by parse() of the derived class
        self.parse(buf)
        self.consumed_bytes = buf.current_position() - pos
        if self.has_children:
            self.parse_children(buf)
        if self.remaining_bytes() > 0:
            if self.boxtype not in Box.data_boxes:
                print("Skipping tailing bytes: Possible parse error (or unhandled box) in %s: consumed %d, skip %d %08x" %(
                    self, self.consumed_bytes, self.remaining_bytes(), buf.peekint(4)))
            buf.skipbytes(self.size - self.consumed_bytes)
            self.consumed_bytes = self.size

    def remaining_bytes(self):
        return self.size - self.consumed_bytes

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

        # Basic sanity check
        if self.parent is not None:
            if self.parent.consumed_bytes + size > self.parent.size:
                raise Exception("Size error: parent %d, consumed %d, child says %d" %(
                    self.parent.size, self.parent.consumed_bytes, size))

        self.size = size
        self.boxtype = boxtype
        self.islarge = islarge
        self.children = []
        # usertype
        if boxtype == 'uuid':
            buf.skipbytes(16)
            self.consumed_bytes += 16

        # free or skip shall be skipped
        if boxtype == 'free' or boxtype == 'skip':
            buf.skipbytes(self.remaining_bytes())
            self.consumed_bytes = self.size

    def parse_children(self, buf):
        while self.consumed_bytes + 8 < self.size:
            try:
                box = Box.getnextbox(buf, self)
                self.children.append(box)
                self.consumed_bytes += box.size
            except Exception as e:
                print(traceback.format_exc())
                print("Error parsing children of %s: %s" %(self, e))
                buf.seekto(self.buffer_offset + self.size)
                self.consumed_bytes = self.size

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

    def basic_info(self):
        yield ("type", self.boxtype)
        yield ("size", self.size)

    def generate_fields(self):
        yield ("size", self.size)

    def __str__(self):
        return "%s (%d bytes)" %(self.boxtype, self.size)

    @staticmethod
    def getnextbox(buf, parent=None):
        from . import movie
        from . import fragment
        from . import flv
        from . import cenc
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

