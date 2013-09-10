#!/usr/bin/python

import os
import sys
import argparse

from datasource import DataBuffer
from console import ConsoleRenderer
from gui import GtkRenderer
from tree import Tree, Attr

def getboxlist(buf, parent=None):
    from isobmff.box import Box
    boxes = []
    try:
        while buf.hasmore():
            box = Box.getnextbox(buf, parent)
            boxes.append(box)
    except:
        import traceback
        print traceback.format_exc()
    return boxes

def get_box_node(box):
    from isobmff.box import Box
    node = Tree(box.boxtype)
    for field in box.generate_fields():
        if isinstance(field, Box):
            add_box(node, field)
        elif type(field) is not tuple:
            raise Exception("Expected a tuple, got a %s" %type(field));
        else:
            node.add_attr(field[0], field[1], field[2] if len(field) == 3 else None)
    return node

# Using python reflection to get the list of properties from boxes.
# The properties are listed in alphabetical order.
# TODO: Handle each box separately and add properties in proper order
#def get_box_node(box):
#    node = Tree(box.boxtype)
#    from isobmff.box import Box
#    for name in dir(box):
#        field = getattr(box, name)
#        if callable(field):
#            continue
#        if name.startswith('__'):
#            continue
#        # skip bookkeeping variables
#        if name in ['boxtype', 'children', 'islarge', 'parent', 'consumed_bytes']:
#            continue
#        if type(field) is list and len(field):
#            if isinstance(field[0], Box):
#                for child in field:
#                    add_box(node, child)
#                continue
#        name = name.replace('_', ' ')
#        node.add_attr(name, field)
#    return node

def add_box(parent, box):
    box_node = parent.add_child(get_box_node(box))
    for child in box.children:
        add_box(box_node, child)
    return box_node


def get_tree_from_file(path):
    try:
        fd = open(path, 'r')
    except:
        raise "Invalid file name %s" %(path)
    boxes = getboxlist(DataBuffer(fd))
    root = Tree(os.path.basename(path))
    for box in boxes:
        add_box(root, box)
    return root


def main():
    parser = argparse.ArgumentParser(
        description='Process iso-bmff file and list the boxes and their contents')
    parser.add_argument('-f', choices=['stdout','gui'], default='stdout',
        help='output format (only stdout is supported as of now)', dest='output_format')
    parser.add_argument('-c', '--color', choices=['on', 'off'], default='on', dest='color',
        help='turn on/off colors in console based output; defaults to true')
    parser.add_argument('input_file', metavar='iso-base-media-file', help='Path to iso media file')
    args = parser.parse_args()

    root = get_tree_from_file(args.input_file)

    renderer = None
    if args.output_format == 'stdout':
        renderer = ConsoleRenderer('  ')
        if args.color == 'off':
            renderer.disable_colors()
    if args.output_format == 'gui':
        renderer = GtkRenderer()

    renderer.render(root)


if __name__ == "__main__":
    main()

