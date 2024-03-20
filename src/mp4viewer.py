#!/usr/bin/env python3
""" The main entry point """

import os
import argparse

from datasource import DataBuffer
from datasource import FileSource
from console import ConsoleRenderer
from tree import Tree

from isobmff.parser import IsobmffParser, getboxdesc
from isobmff.box import Box

def get_box_node(box, args):
    """ Get a tree node representing the box """
    node = Tree(box.boxtype, getboxdesc(box.boxtype))
    for field in box.generate_fields():
        if isinstance(field, Box):
            add_box(node, field, args)
        elif not isinstance(field, tuple):
            raise TypeError(f"Expected a tuple, got a {type(field)}")
        else:
            # generate fields yields a tuple of order (name, value, [formatted_value])
            value = field[1]
            if args.truncate and isinstance(value, list) and len(value) > 16:
                first3 = ','.join([str(i) for i in value[:3]])
                last3 = ','.join([str(i) for i in value[-3:]])
                value = f"[{first3} ... {last3}] {len(value)} items"
            node.add_attr(field[0], value, field[2] if len(field) == 3 else None)
    return node

def add_box(parent, box, args):
    """ Add the box and its children to the tree """
    box_node = parent.add_child(get_box_node(box, args))
    for child in box.children:
        add_box(box_node, child, args)
    return box_node


def get_tree_from_file(path, args):
    """ Parse the mp4 file and return a tree of boxes """
    with open(path, 'rb') as fd:
        # isobmff file parser
        parser = IsobmffParser(DataBuffer(FileSource(fd)), args.debug)
        boxes = parser.getboxlist()
    root = Tree(os.path.basename(path), "File")
    for box in boxes:
        add_box(root, box, args)
    return root


def main():
    """ the main """
    parser = argparse.ArgumentParser(
        description='Process iso-bmff file and list the boxes and their contents')
    parser.add_argument('-o', '--output', choices=['stdout','gui'], default='stdout',
        help='output format', dest='output_format')
    parser.add_argument('-e', '--expand-arrays', action='store_false',
        help='do not truncate long arrays', dest='truncate')
    parser.add_argument('-c', '--color', choices=['on', 'off'], default='on', dest='color',
        help='turn on/off colors in console based output; on by default')
    parser.add_argument('--debug', action='store_true', help='Used for internal debugging')
    parser.add_argument('--latex', action='store_true',
                        help='Generate latex-in-markdown for github README')
    parser.add_argument('input_file', metavar='iso-base-media-file', help='Path to iso media file')
    args = parser.parse_args()

    root = get_tree_from_file(args.input_file, args)

    renderer = None
    if args.output_format == 'stdout':
        renderer = ConsoleRenderer('  ', latex_md_for_github=args.latex)
        if args.color == 'off':
            renderer.disable_colors()
        else:
            renderer.update_colors()
    if args.output_format == 'gui':
        # pylint: disable=import-outside-toplevel
        from gui import GtkRenderer
        renderer = GtkRenderer()

    renderer.render(root)


if __name__ == "__main__":
    main()
