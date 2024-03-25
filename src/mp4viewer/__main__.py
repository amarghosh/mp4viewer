""" The main entry point """

import os
import sys
import argparse

from mp4viewer.tree import Tree
from mp4viewer.datasource import FileSource, DataBuffer
from mp4viewer.console import ConsoleRenderer
from mp4viewer.json_renderer import JsonRenderer

from mp4viewer.isobmff.parser import IsobmffParser, getboxdesc
from mp4viewer.isobmff.box import Box


def get_box_node(box, args):
    """Get a tree node representing the box"""
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
                first3 = ",".join([str(i) for i in value[:3]])
                last3 = ",".join([str(i) for i in value[-3:]])
                value = f"[{first3} ... {last3}] {len(value)} items"
            node.add_attr(field[0], value, field[2] if len(field) == 3 else None)
    return node


def add_box(parent, box, args):
    """Add the box and its children to the tree"""
    box_node = parent.add_child(get_box_node(box, args))
    for child in box.children:
        add_box(box_node, child, args)
    return box_node


def get_tree_from_file(path, args):
    """Parse the mp4 file and return a tree of boxes"""
    with open(path, "rb") as fd:
        # isobmff file parser
        parser = IsobmffParser(DataBuffer(FileSource(fd)), args.debug)
        boxes = parser.getboxlist()
    root = Tree(os.path.basename(path), "File")
    for box in boxes:
        add_box(root, box, args)
    return root


def main():
    """the main"""
    parser = argparse.ArgumentParser(
        description="Parse mp4 files (ISO bmff) and view the boxes and their contents.  "
        "The output can be viewed on the console, a window, or saved in to a json file."
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["stdout", "gui", "json"],
        default="stdout",
        help="Specify the output format. Please note that pygtk is required for `gui`. ",
        dest="output_format",
    )
    parser.add_argument(
        "-c",
        "--color",
        choices=["on", "off"],
        default="on",
        dest="color",
        help="Toggle colors in console based output; on by default.",
    )
    parser.add_argument(
        "-j",
        "--json",
        dest="json_path",
        help="Path to the json file where the output should be saved. If this is specified, "
        "the json output will be generated and written to this file even if the requested "
        "output format is not json. If the output format is json and this argument is not "
        "specified, the json object will be written to the current directory using "
        '"$PWD/$(basename input_file).mp4viewer.json"',
    )
    parser.add_argument(
        "-e",
        "--expand-arrays",
        action="store_false",
        help="Do not truncate long arrays",
        dest="truncate",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Used for internal debugging"
    )
    parser.add_argument(
        "--latex",
        action="store_true",
        help="Generate latex-in-markdown for github README",
    )
    parser.add_argument("input_file", help="Location of the ISO bmff file (mp4)")
    args = parser.parse_args()

    root = get_tree_from_file(args.input_file, args)

    renderer = None
    if args.output_format == "stdout":
        renderer = ConsoleRenderer(latex_md_for_github=args.latex)
        if args.color == "off":
            renderer.disable_colors()
        else:
            renderer.update_colors()

    if args.output_format == "gui":
        # pylint: disable=import-outside-toplevel
        from .gui import GtkRenderer

        renderer = GtkRenderer()

    if args.output_format == "json":
        renderer = JsonRenderer(mp4_path=args.input_file, output_path=args.json_path)

    renderer.render(root)

    # Handle the case where json output is required in addition to the requested format
    if args.json_path is not None and args.output_format != "json":
        JsonRenderer(mp4_path=args.input_file, output_path=args.json_path).render(root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
