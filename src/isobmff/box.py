""" defines basic box classes Box, FullBox and FileType """

# pylint: disable=too-many-instance-attributes

import traceback
import sys

def _error_print(s):
    print(s, file=sys.stderr)

class Box:
    """
    Base class for all boxes.
    Subclasses representing pure containers should set the is_container flag.
    Boxes with data and children should handle their children from their own parse() overrides.
    """

    # Avoid printing parsing errors for known data boxes
    data_boxes = ['mdat', 'udta']

    def __init__(self, parser, parent=None, is_container = False):
        self.parent = parent
        buf = parser.buf
        pos = buf.current_position()
        self.buffer_offset = pos
        self.has_children = is_container
        # has_children can be updated by parse() of the derived class
        self.parse(parser)
        self.consumed_bytes = buf.current_position() - pos
        if self.has_children:
            self.parse_children(parser)
        if self.remaining_bytes() > 0:
            if self.boxtype not in Box.data_boxes:
                print(f"Skipping tailing bytes: Possible parse error (or unhandled box) in {self}"
                    f": consumed {self.consumed_bytes}, skip {self.remaining_bytes()} "
                    f"{buf.peekint(4):08x}")
            try:
                self._skip_remaining_bytes(buf)
                assert self.consumed_bytes == self.size, f'{self} size error'
            except BufferError:
                _error_print(f"\nInvalid data in box {self.boxtype} at {self.buffer_offset}")
                remaining_bytes = self._remaining_bytes(buf)
                overflow = buf.current_position() + remaining_bytes - len(buf)
                _error_print(f"Attempt to skip {remaining_bytes} bytes from "
                        f"{buf.current_position()}, but the file is only {len(buf)} bytes; "
                        f"overflow by {overflow} bytes")
                _error_print("It is possible that the file was truncated by an incomplete download,"
                        " or it was generated using a slightly buggy encoder")
                _error_print("You can use ffmpeg to get more details:"
                        "`ffmpeg -v error -i file.mp4 -f null - `")
                parser.dump_remaining_fourccs()
                _error_print(f"skipping the remaining {buf.remaining_bytes()} bytes")
                buf.skipbytes(buf.remaining_bytes())

    def _remaining_bytes(self, buf):
        if self.size == 0:
            bytes_to_skip = buf.remaining_bytes()
        else:
            bytes_to_skip = self.size - self.consumed_bytes
        return bytes_to_skip


    def _skip_remaining_bytes(self, buf):
        bytes_to_skip = self._remaining_bytes(buf)
        buf.skipbytes(bytes_to_skip)
        self.consumed_bytes += bytes_to_skip


    def remaining_bytes(self):
        """
        Returns the number of bytes remaining to be consumed.
        The subclasses should keep updating the `consumed_bytes` along the parse() method
        to keep this value accurate.
        """
        if self.size == 0:
            raise AssertionError(f'Box {self}: remaining_bytes not supported for size0')
        return self.size - self.consumed_bytes

    def parse(self, parse_ctx):
        """
        Parse this box from the parse_ctx.
        Subclasses should override this and invoke super().parse() before proceeding with their own
        parsing logic.
        """
        buf = parse_ctx.buf
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
                # pylint: disable=consider-using-f-string
                raise AssertionError("Size error: parent %d, consumed %d, child says %d" %(
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
        if boxtype in ('free', 'skip'):
            buf.skipbytes(self.remaining_bytes())
            self.consumed_bytes = self.size

    def parse_children(self, parser):
        """
        Parse all child boxes of this container.
        This is called from the super().parse()
        """
        buf = parser.buf
        while self.consumed_bytes + 8 < self.size:
            try:
                box = parser.getnextbox(self)
                self.children.append(box)
                self.consumed_bytes += box.size
            except AssertionError as e:
                print(traceback.format_exc())
                print(f"Error parsing children of {self}: {e}")
                buf.seekto(self.buffer_offset + self.size)
                self.consumed_bytes = self.size

    def find_ancestor(self, boxtype):
        """
        Get the first direct ancestor with a matching `boxtype`, or None
        """
        p = self.parent
        while p is not None:
            if p.boxtype == boxtype:
                return p
            p = p.parent
        return None

    def find_child(self, boxtype):
        """ Get the first child with the matching boxtype """
        for child in self.children:
            if child.boxtype == boxtype:
                return child
        return None

    def generate_fields(self):
        """
        Generator that yields either boxes or tuples.
        Each tuple shall be or format (name-of-field, actual-value, <optional display value>).
        Subclasses shall call super().generate_fields() from the overriden functions.
        """
        yield ("size", self.size)

    def __str__(self):
        return f"{self.boxtype} ({self.size} bytes)"


class FullBox(Box):
    """ base class for boxes with version and flags """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.version = buf.readbyte()
        self.flags = buf.readint(3)
        self.consumed_bytes += 4

    def generate_fields(self):
        super().generate_fields()
        yield ("version", self.version)
        yield ("flags", f"0x{self.flags:06X}")


class FileType(Box):
    """ ftyp """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.major_brand = buf.readstr(4)
        self.minor_version = buf.readint32()
        self.consumed_bytes += 8
        self.brands = []
        while self.consumed_bytes < self.size:
            self.brands.append(buf.readstr(4))
            self.consumed_bytes += 4

    def generate_fields(self):
        super().generate_fields()
        yield ("major brand", self.major_brand)
        yield ("minor version", self.minor_version)
        yield ("brands", ','.join(self.brands))

    def __str__(self):
        # pylint: disable=consider-using-f-string
        return "%s %s %d with %d brands %s" %(
                super().__str__(), self.major_brand, self.minor_version, len(self.brands),
                ','.join(self.brands)
            )
