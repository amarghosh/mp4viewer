#!/usr/bin/env python3

import os
import argparse

from datasource import DataBuffer
from datasource import FileSource
from console import ConsoleRenderer
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
        print(traceback.format_exc())
    return boxes

def get_box_node(box, args):
    from isobmff.box import Box
    node = Tree(box.boxtype, Box.getboxdesc(box.boxtype))
    for field in box.generate_fields():
        if isinstance(field, Box):
            add_box(node, field, args)
        elif type(field) is not tuple:
            raise Exception("Expected a tuple, got a %s" %type(field))
        else:
            #generate fields yields a tuple of order (name, value, [formatted_value])
            value = field[1]
            if args.truncate and type(value) is list and len(value) > 10:
                value = "[%s ... %s] %d items" %(
                    ','.join([str(i) for i in value[:3]]),
                    ','.join([str(i) for i in value[-3:]]),
                    len(value),
                )
            node.add_attr(field[0], value, field[2] if len(field) == 3 else None)
    return node

def add_box(parent, box, args):
    box_node = parent.add_child(get_box_node(box, args))
    for child in box.children:
        add_box(box_node, child, args)
    return box_node


def get_tree_from_file(path, args):
    with open(path, 'rb') as fd:
        boxes = getboxlist(DataBuffer(FileSource(fd)))
    root = Tree(os.path.basename(path), "File")
    for box in boxes:
        add_box(root, box, args)
    return root


def main():
    parser = argparse.ArgumentParser(
        description='Process iso-bmff file and list the boxes and their contents')
    parser.add_argument('-o', choices=['stdout','gui'], default='stdout',
        help='output format', dest='output_format')
    parser.add_argument('-e', '--expand-arrays', action='store_false',
        help='do not truncate long arrays', dest='truncate')
    parser.add_argument('-c', '--color', choices=['on', 'off'], default='on', dest='color',
        help='turn on/off colors in console based output; on by default')
    parser.add_argument('input_file', metavar='iso-base-media-file', help='Path to iso media file')
    args = parser.parse_args()

    root = get_tree_from_file(args.input_file, args)

    renderer = None
    if args.output_format == 'stdout':
        renderer = ConsoleRenderer('  ')
        if args.color == 'off':
            renderer.disable_colors()
    if args.output_format == 'gui':
        from gui import GtkRenderer
        renderer = GtkRenderer()

    renderer.render(root)


if __name__ == "__main__":
    main()

