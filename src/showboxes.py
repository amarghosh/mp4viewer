#!/usr/bin/python

import os
import argparse

from datasource import DataBuffer
from isobmff.box import getboxlist


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

    for b in boxes:
        b.display('')


if __name__ == "__main__":
    main()

