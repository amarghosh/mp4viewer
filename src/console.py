import sys
from tree import Tree, Attr

def write(s):
    sys.stdout.write(s)

class ConsoleRenderer(object):
    VERT = '!'
    HORI = '-'
    COLOR_HEADER = '\033[31m'
    COLOR_ATTR = '\033[36m'
    ENDCOL = '\033[0m'

    def __init__(self, offset=None, indent_unit='    ', have_children=False):
        self.offset = '' if offset is None else offset
        self.indent_unit = indent_unit
        self.header_prefix = '`' + indent_unit.replace(' ', ConsoleRenderer.HORI)[1:]

    def show_node(self, node, prefix):
        write("%s%s%s%s%s\n" %(prefix, self.header_prefix, ConsoleRenderer.COLOR_HEADER,
            node.name, ConsoleRenderer.ENDCOL))
        if len(node.children):
            data_prefix = prefix + self.indent_unit[:-1] + ConsoleRenderer.VERT + self.indent_unit
        else:
            data_prefix = prefix + self.indent_unit + self.indent_unit
        for attr in node.attrs:
            if attr.display_value != None:
                write("%s%s%s%s: %s (%s)\n" %(data_prefix, ConsoleRenderer.COLOR_ATTR, attr.name,
                    ConsoleRenderer.ENDCOL, attr.value, attr.display_value))
            else:
                write("%s%s%s%s: %s\n" %(data_prefix, ConsoleRenderer.COLOR_ATTR, attr.name,
                    ConsoleRenderer.ENDCOL, attr.value))
        child_indent = prefix + self.indent_unit[:-1] + ConsoleRenderer.VERT
        for i in range(len(node.children)):
            if i + 1 == len(node.children):
                child_indent = prefix + self.indent_unit
            self.show_node(node.children[i], child_indent)

    def render(self, tree):
        self.show_node(tree, self.offset)

    def updatecolors():
        if not sys.stdout.isatty():
            ConsoleRenderer.disable_colors()

    def disable_colors(self):
            ConsoleRenderer.COLOR_HEADER = ''
            ConsoleRenderer.COLOR_ATTR = ''
            ConsoleRenderer.ENDCOL = ''

