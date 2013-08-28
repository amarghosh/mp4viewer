#!/usr/bin/python

import os
import sys
import argparse

from datasource import DataBuffer
from isobmff.box import getboxlist

class FormatInfo(object):
    VERT = '!'
    HORI = '-'
    COLOR_HEADER = '\033[31m'
    COLOR_ATTR = '\033[36m'
    ENDCOL = '\033[0m'

    @staticmethod
    def updatecolors():
        if not sys.stdout.isatty():
            FormatInfo.COLOR_HEADER = ''
            FormatInfo.COLOR_ATTR = ''
            FormatInfo.ENDCOL = ''

    def __init__(self, offset=None, indent_unit='    ', have_children=False):
        self.offset = '' if offset is None else offset
        self.indent_unit = indent_unit
        self.update(have_children)

    def update(self, have_children):
        if have_children:
            self.have_children = True
            self.data_prefix = self.offset + self.indent_unit[:-1] + FormatInfo.VERT + self.indent_unit
        else:
            self.have_children = False
            self.data_prefix = self.offset + self.indent_unit + self.indent_unit
        self.header_prefix = self.offset + '`' + self.indent_unit.replace(' ', FormatInfo.HORI)[1:]

    def set_siblingstatus(self, value=False):
        if value:
            self.offset = self.offset[:-1] + FormatInfo.VERT
        else:
            self.offset = self.offset[:-1] + ' '
        self.update(self.have_children)

    def get_next(self, have_children=False):
        newoffset = self.offset + self.indent_unit
        if self.have_children:
            newoffset = newoffset[:-1] + FormatInfo.VERT
        return FormatInfo(newoffset, self.indent_unit, have_children)

    def add_header(self, text):
        return self.header_prefix + FormatInfo.COLOR_HEADER + text + FormatInfo.ENDCOL + '\n'

    def add_data(self, text):
        return self.data_prefix + text + '\n'

    def add_attr(self, key, value):
        return self.data_prefix + FormatInfo.COLOR_ATTR + key + FormatInfo.ENDCOL + ": %s\n" %(str(value))


def main():
    parser = argparse.ArgumentParser(description='Process isobmff file and list the boxes and their contents')
    parser.add_argument('input_file', metavar='file', help='Path to iso media file')
    args = parser.parse_args()
    try:
        size = os.stat(args.input_file).st_size
        f = open(args.input_file, 'r')
    except:
        print "Invalid file name %s" %(args.input_file)
        return 2

    buf = DataBuffer(f)
    boxes = getboxlist(buf)

    FormatInfo.updatecolors()

    fmt = FormatInfo('  ')
    fmt.set_siblingstatus(True)
    for i in range(len(boxes)):
        if i == len(boxes) - 1:
            fmt.set_siblingstatus(False);
        boxes[i].display(fmt)


if __name__ == "__main__":
    main()

