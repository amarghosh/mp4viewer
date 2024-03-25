""" Adobe FLV format related boxes """

# pylint: disable=too-many-instance-attributes

from . import box


class AdobeFragmentRandomAccess(box.FullBox):
    """afra"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        val = buf.readbyte()
        self.long_ids = val & 0x80 != 0
        self.long_offsets = val & 0x40 != 0
        self.global_entries_present = val & 0x20 != 0
        self.timescale = buf.readint32()
        self.entry_count = buf.readint32()
        self.entries = []
        for _ in range(self.entry_count):
            time = buf.readint64()
            if self.long_offsets:
                offset = buf.readint64()
            else:
                offset = buf.readint32()
            self.entries.append((time, offset))
        self.global_entry_count = 0
        self.global_entries = []
        if self.global_entries_present:
            self.global_entry_count = buf.readint32()
        for _ in range(self.global_entry_count):
            time = buf.readint64()
            if self.long_ids:
                eid = buf.readint32()
            else:
                eid = buf.readint16()
            self.global_entries.append((time, eid))

    def generate_fields(self):
        yield from super().generate_fields()
        yield ("Long IDs", self.long_ids)
        yield ("Long offsets", self.long_offsets)
        yield ("Global entries present", self.global_entries_present)
        yield ("Timescale", self.timescale)
        yield ("Entry count", self.entry_count)
        for i, e in enumerate(self.entries):
            yield (f"  Entry {i+1}", f"time={e[0]}, offset={e[1]}")
        if self.global_entries_present:
            yield ("Global entry count", self.global_entry_count)
            for i, e in enumerate(self.global_entries):
                yield (f"  Global entry {i+1}", f"time={e[0]}, id={e[1]}")


class AdobeBootstrap(box.FullBox):
    """abst"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        self.bootstrap_info_version = buf.readint32()
        val = buf.readbyte()
        self.profile = (val & 0xC0) >> 6
        self.live = val & 0x40 != 0
        self.update = val & 0x20 != 0
        self.timescale = buf.readint32()
        self.current_media_time = buf.readint64()
        self.smpte_time_code_offset = buf.readint64()
        self.movie_id = buf.read_cstring()[0]
        self.server_entry_count = buf.readbyte()
        self.server_entries = []
        for _ in range(self.server_entry_count):
            self.server_entries.append(buf.read_cstring()[0])
        self.quality_entry_count = buf.readbyte()
        self.quality_entries = []
        for _ in range(self.quality_entry_count):
            self.quality_entries.append(buf.read_cstring()[0])
        self.drmdata = buf.read_cstring()[0]
        self.metadata = buf.read_cstring()[0]
        self.segment_run_table_entry_count = buf.readbyte()
        self.segment_run_table_entries = []
        for _ in range(self.segment_run_table_entry_count):
            self.segment_run_table_entries.append(AdobeSegmentRunTable(buf))
        self.fragment_run_table_entry_count = buf.readbyte()
        self.fragment_run_table_entries = []
        for _ in range(self.fragment_run_table_entry_count):
            self.fragment_run_table_entries.append(AdobeFragmentRunTable(buf))

    def generate_fields(self):
        yield from super().generate_fields()
        yield ("Profile", self.profile)
        yield ("Live", self.live)
        yield ("Update", self.update)
        yield ("Timescale", self.timescale)
        yield ("Current media time", self.current_media_time)
        yield ("SMPTE time code", self.smpte_time_code_offset)
        yield ("Movie ID", self.movie_id if len(self.movie_id) else "<empty>")
        yield ("Server entry count", self.server_entry_count)
        for s in self.server_entries:
            yield ("Server", s if len(s) else "<empty>")
        yield ("Quality entry count", self.quality_entry_count)
        for q in self.quality_entries:
            yield ("Quality", q if len(q) else "<empty>")
        yield ("DRM data", self.drmdata if len(self.drmdata) else "<empty>")
        yield ("Metadata", self.metadata if len(self.metadata) else "<empty>")
        yield ("Segment run table entry count", self.segment_run_table_entry_count)
        yield from self.segment_run_table_entries
        yield ("Fragment run table entry count", self.fragment_run_table_entry_count)
        yield from self.fragment_run_table_entries


class AdobeSegmentRunTable(box.FullBox):
    """asrt"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        self.quality_entry_count = buf.readbyte()
        self.quality_url_modifiers = []
        for _ in range(self.quality_entry_count):
            self.quality_url_modifiers.append(buf.read_cstring()[0])
        self.segment_entry_count = buf.readint32()
        self.segment_entries = []
        for _ in range(self.segment_entry_count):
            first_segment = buf.readint32()
            fragments_per_segment = buf.readint32()
            self.segment_entries.append((first_segment, fragments_per_segment))

    def generate_fields(self):
        yield from super().generate_fields()
        yield ("Quality entry count", self.quality_entry_count)
        for q in self.quality_url_modifiers:
            yield ("Quality url modifier", q if len(q) else "<empty>")
        yield ("Segment entry count", self.segment_entry_count)
        for idx, e in enumerate(self.segment_entries):
            yield (
                f"Entry {idx+1}",
                f"First segment={e[0]}, Fragments per segment={e[1]}",
            )


class AdobeFragmentRunTable(box.FullBox):
    """afrt"""

    def parse(self, parse_ctx):
        super().parse(parse_ctx)
        buf = parse_ctx.buf
        self.timescale = buf.readint32()
        self.quality_entry_count = buf.readbyte()
        self.quality_url_modifiers = []
        for _ in range(self.quality_entry_count):
            self.quality_url_modifiers.append(buf.read_cstring()[0])
        self.fragment_entry_count = buf.readint32()
        self.fragment_entries = []
        for _ in range(self.fragment_entry_count):
            first_fragment = buf.readint32()
            first_fragment_timestamp = buf.readint64()
            fragment_duration = buf.readint32()
            discontinuity_idicator = 0
            if fragment_duration == 0:
                discontinuity_idicator = buf.readbyte()
            self.fragment_entries.append(
                (
                    first_fragment,
                    first_fragment_timestamp,
                    fragment_duration,
                    discontinuity_idicator,
                )
            )

    def generate_fields(self):
        yield from super().generate_fields()
        yield ("Timescale", self.timescale)
        yield ("Quality entry count", self.quality_entry_count)
        for q in self.quality_url_modifiers:
            yield ("Quality url modifier", q if len(q) else "<empty>")
        yield ("Fragment entry count", self.fragment_entry_count)
        for i, e in enumerate(self.fragment_entries):
            yield (
                f"Entry {i+1}",
                f"first fragment={e[0]}, first fragment timestamp={e[1]}, "
                f"fragment duration={e[2]}, discontinuity={e[3]}",
            )


boxmap = {
    "afra": AdobeFragmentRandomAccess,
    "abst": AdobeBootstrap,
    "asrt": AdobeSegmentRunTable,
    "afrt": AdobeFragmentRunTable,
}
