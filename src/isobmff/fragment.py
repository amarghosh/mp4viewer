""" movie fragment related boxes """
# pylint: disable=too-many-instance-attributes

from . import box

class MovieFragmentHeader(box.FullBox):
    """ mfhd """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.sequence_number = buf.readint32()

    def generate_fields(self):
        super().generate_fields()
        yield ("Sequence number", self.sequence_number)


class TrackFragmentHeader(box.FullBox):
    """ tfhd """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.track_id = buf.readint32()
        if self.flags & 0x000001:
            self.base_data_offset = buf.readint64()
        if self.flags & 0x000002:
            self.sample_description_index = buf.readint32()
        if self.flags & 0x000008:
            self.default_sample_duration = buf.readint32()
        if self.flags & 0x000010:
            self.default_sample_size = buf.readint32()
        if self.flags & 0x000020:
            self.default_sample_flags = buf.readint32()
        self.duration_is_empty = self.flags & 0x010000 != 0
        self.default_base_is_moof = self.flags & 0x020000 != 0

    def generate_fields(self):
        super().generate_fields()
        yield ("Track id", self.track_id)
        if self.flags & 0x000001:
            yield("Base data offset", self.base_data_offset)
        if self.flags & 0x000002:
            yield("Sample description index", self.sample_description_index)
        if self.flags & 0x000008:
            yield("Default sample duration", self.default_sample_duration)
        if self.flags & 0x000010:
            yield("Default sample size", self.default_sample_size)
        if self.flags & 0x000020:
            yield("Default sample flags", f"{self.default_sample_flags:08x}")
        yield("Duration is empty", self.duration_is_empty)
        yield("Default base is moof", self.default_base_is_moof)


class TrackFragmentRun(box.FullBox):
    """ trun """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.sample_count = buf.readint32()
        if self.flags & 0x000001:
            self.data_offset = buf.readint32()
        if self.flags & 0x000004:
            self.first_sample_flags = buf.readint32()
        self.samples = []
        for _ in range(self.sample_count):
            dur = 0
            size = 0
            flags = 0
            off = 0
            if self.flags & 0x000100:
                dur = buf.readint32()
            if self.flags & 0x000200:
                size = buf.readint32()
            if self.flags & 0x000400:
                flags = buf.readint32()
            if self.flags & 0x000800:
                if self.version == 0:
                    off = buf.readint32()
                else:
                    #signed, so do the two's complement
                    off = buf.readint32()
                    if off & 0x80000000:
                        off = -1 * ((off^0xffffffff) + 1)
            self.samples.append((dur,size,flags,off))

    def generate_fields(self):
        super().generate_fields()
        yield('Sample count', self.sample_count)
        if self.flags & 0x000001:
            yield('Data offset', self.data_offset)
        if self.flags & 0x000004:
            yield('First sample flags', f"{self.first_sample_flags:08x}")
        i = 0
        for s in self.samples:
            i += 1
            vals = []
            if self.flags & 0x000100:
                vals.append(f"duration={s[0]}")
            if self.flags & 0x000200:
                vals.append(f"size={s[1]}")
            if self.flags & 0x000400:
                vals.append(f"flags=0x{s[2]:08x}")
            if self.flags & 0x000800:
                vals.append(f"compositional time offset={s[3]}")
            yield (f'  Sample {i}', ', '.join(vals))


class SampleAuxInfoSizes(box.FullBox):
    """ saiz """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        if self.flags & 1:
            self.aux_info_type = buf.readint32()
            self.aux_info_type_parameter = buf.readint32()
        self.default_sample_info_size = buf.readbyte()
        self.sample_count = buf.readint32()
        self.samples = []
        if self.default_sample_info_size == 0:
            for _ in range(self.sample_count):
                self.samples.append(buf.readbyte())

    def generate_fields(self):
        super().generate_fields()
        if self.flags & 1:
            yield("Aux info type", self.aux_info_type)
            yield("Aux info type parameter", self.aux_info_type_parameter)
        if self.default_sample_info_size:
            yield ("Default sample info size", self.default_sample_info_size)
        else:
            for sample in self.samples:
                yield("  Sample info size", sample)


class SampleAuxInfoOffsets(box.FullBox):
    """ saio """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        if self.flags & 1:
            self.aux_info_type = buf.readint32()
            self.aux_info_type_parameter = buf.readint32()
        self.entry_count = buf.readint32()
        self.offsets = []
        if self.version == 0:
            for _ in range(self.entry_count):
                self.offsets.append(buf.readint32())
        else:
            for _ in range(self.entry_count):
                self.offsets.append(buf.readint64())

    def generate_fields(self):
        super().generate_fields()
        if self.flags & 1:
            yield("Aux info type", self.aux_info_type)
            yield("Aux info type parameter", self.aux_info_type_parameter)
        yield("Entry Count", self.entry_count)
        for offset in self.offsets:
            yield("  Offset", offset)


class TrackFragmentDecodeTime(box.FullBox):
    """ tfdt """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        if self.version == 1:
            self.decode_time = buf.readint64()
        else:
            self.decode_time = buf.readint32()

    def generate_fields(self):
        super().generate_fields()
        yield ("Base media decode time", self.decode_time)


class SegmentType(box.FileType):
    """
    Box type: styp
    The definition of the segment type box is same as the file type box
    """


class SegmentIndexBox(box.FullBox):
    """ sidx """
    def parse(self, parse_ctx):
        buf = parse_ctx.buf
        super().parse(parse_ctx)
        self.reference_id = buf.readint32()
        self.timescale = buf.readint32()
        if self.version == 0:
            self.earliest_presentation_time = buf.readint32()
            self.first_offset = buf.readint32()
        else:
            self.earliest_presentation_time = buf.readint64()
            self.first_offset = buf.readint64()
        buf.skipbytes(2)
        self.references = []
        self.reference_count = buf.readint16()
        for _ in range(self.reference_count):
            val = buf.readint32()
            ref_type = (val & 0x80000000) >> 31
            ref_size = val & 0x7FFFFFFF
            ref_duration = buf.readint32()
            val = buf.readint32()
            starts_with_sap = (val & 0x80000000) != 0
            sap_type = (val & 0x70000000) >> 28
            sap_delta_time = val & 0x0FFFFFFF
            self.references.append(
                    (ref_type, ref_size, ref_duration,
                        starts_with_sap, sap_type, sap_delta_time))

    def generate_fields(self):
        # pylint: disable=consider-using-f-string
        super().generate_fields()
        yield('Reference ID', self.reference_id)
        yield('Timescale', self.timescale)
        yield('Earliest presentation time', self.earliest_presentation_time)
        yield('First offset', self.first_offset)
        yield('Reference count', self.reference_count)
        i = 0
        for ref in self.references:
            i += 1
            yield(f'  Reference {i}', f'type={ref[0]}, size={ref[1]}, duration={ref[2]}, ' \
                    f'starts with SAP={ref[3]}, SAP type={ref[4]}, SAP delta time={ref[5]}')


boxmap = {
        #'mfra' : MovieFragmentRandomAccessBox
        'mfhd' : MovieFragmentHeader,
        'tfhd' : TrackFragmentHeader,
        'trun' : TrackFragmentRun,
        'saiz' : SampleAuxInfoSizes,
        'saio' : SampleAuxInfoOffsets,
        'tfdt' : TrackFragmentDecodeTime,
        'styp' : SegmentType,
        'sidx' : SegmentIndexBox,
        #'ssix' : SubsegmentIndexBox,
    }
