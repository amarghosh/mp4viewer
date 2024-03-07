""" isobmff parser public interface """

import traceback
from datasource import DataBuffer
from . import box, movie, fragment, flv, cenc

class IsobmffParser:
    """ Parser class """
    container_boxes = [
        'moov', 'trak', 'edts', 'mdia', 'minf', 'dinf', 'stbl', 'mvex',
        'moof', 'traf', 'mfra', 'skip', 'meta', 'ipro', 'sinf', 'schi',
    ]
    def __init__(self, buf:DataBuffer, debug=False):
        boxmap = {
            'ftyp' : box.FileType,
        }
        boxmap.update(movie.boxmap)
        boxmap.update(fragment.boxmap)
        boxmap.update(flv.boxmap)
        boxmap.update(cenc.boxmap)
        self.boxmap = boxmap
        self.buf = buf
        self.debug = debug

    def getboxlist(self):
        """ returns a list of all boxes in the input stream """
        boxes = []
        try:
            while self.buf.hasmore():
                next_box = self.getnextbox(None)
                boxes.append(next_box)
        except (AssertionError, TypeError):
            print(traceback.format_exc())
        return boxes

    def getnextbox(self, parent:box.Box):
        """ returns the next box in the stream """
        fourcc = self.buf.peekstr(4, 4)
        if fourcc in self.boxmap:
            next_box = self.boxmap[fourcc](self, parent)
        else:
            is_container = fourcc in self.container_boxes
            next_box = box.Box(self, parent, is_container)
        return next_box

    def dump_remaining_fourccs(self):
        """
        Scan through the bytestream and print potential box types and their sizes.
        Hopefully, this can be used for debugging our parser errors.
        This is a work in progress.
        """
        if not self.debug:
            print("Detected potential parse error; run with --debug to see more info")
            return
        print("\nBuffer error detected; scanning through the file looking for boxes."
                "This will take time as we need to go through every byte.\n")
        buf = self.buf
        known_boxtypes = set(list(self.boxmap) + list(box_names))
        while buf.remaining_bytes() >= 4:
            fourcc = buf.peekint(4)
            if (fourcc & 0x80) | (fourcc & 0x8000) | (fourcc & 0x800000) | (fourcc & 0x80000000):
                buf.skipbytes(1)
                continue
            fourcc = buf.peekstr(4)
            if fourcc in known_boxtypes:
                buf.seekto(buf.current_position() - 4)
                sz = buf.readint32()
                remaining_bytes = buf.remaining_bytes() - 4
                if sz <= remaining_bytes:
                    print(f"Possible box {fourcc} at {buf.current_position()} of size {sz}")
                else:
                    delta = buf.current_position() + sz - len(buf.source)
                    print(f"boxtype {fourcc} at {buf.current_position()} of size {sz} but "
                            f"overflows by {delta}")
                buf.skipbytes(4)
            else:
                buf.skipbytes(1)


# fourcc -> human readable description map
box_names = {
    # iso bmff box types
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
    # common encryption boxes
    'tenc' : 'Track encryption box',
    'senc' : 'Sample encryption box',
    'pssh' : 'Protection system specific header box',
    'schm' : 'Scheme type box',
    'schi' : 'Scheme information box',
    'sinf' : 'Protection scheme information box',
    'frma' : 'Original format box',
    # flv specific boxes
    'afra' : 'Adobe fragment random access box',
    'abst' : 'Adobe bootstrap info box',
    'asrt' : 'Adobe segment run table box',
    'afrt' : 'Adobe fragment run table box',
}

def getboxdesc(name):
    """ get box description for the given fourcc """
    return box_names[name] if name in box_names else name.upper()
