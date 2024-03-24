""" Console renderer """

import sys

from mp4viewer.tree import Tree


def _write(s):
    sys.stdout.write(s)


class ConsoleRenderer:
    """Prints output to the console"""

    VERT = "!"
    HORI = "-"
    COLOR_HEADER = "\033[31m"
    COLOR_ATTR = "\033[36m"
    COLOR_SUB_TEXT = "\033[38;5;243m"
    ENDCOL = "\033[0m"

    def __init__(self, offset=None, indent_unit="    ", latex_md_for_github=False):
        self.offset = "" if offset is None else offset
        self.indent_unit = indent_unit
        self.header_prefix = "`" + indent_unit.replace(" ", ConsoleRenderer.HORI)[1:]
        self.use_colors = True
        self.eol = "\n"
        self.indent_with_vert = self.indent_unit[:-1] + ConsoleRenderer.VERT
        if latex_md_for_github:
            self._enable_latex_md_for_github()

    def _enable_latex_md_for_github(self):
        self.offset = self.offset.replace(" ", "&nbsp;")
        self.indent_unit = self.indent_unit.replace(" ", "&nbsp;")
        self.header_prefix = "\\`" + self.header_prefix[1:]
        self.eol = "  \n"
        self.indent_with_vert = (
            self.indent_unit[: -len("&nbsp;")] + ConsoleRenderer.VERT
        )
        ConsoleRenderer.COLOR_HEADER = " ${\\textsf{\\color{red}"
        ConsoleRenderer.COLOR_ATTR = " ${\\textsf{\\color{blue}"
        ConsoleRenderer.COLOR_SUB_TEXT = " ${\\textsf{\\color{grey}"
        ConsoleRenderer.ENDCOL = "}}$"

    def _wrap_color(self, text, color):
        suffix = ConsoleRenderer.ENDCOL if self.use_colors else ""
        return f"{color}{text}{suffix}"

    def _sub_text(self, text):
        if self.use_colors:
            wrapped_text = self._wrap_color(text, ConsoleRenderer.COLOR_SUB_TEXT)
        else:
            wrapped_text = f"<{text}>"
        return wrapped_text

    def show_node(self, node, prefix):
        """recursively display the node"""
        header_color = ConsoleRenderer.COLOR_HEADER if self.use_colors else ""
        attr_color = ConsoleRenderer.COLOR_ATTR if self.use_colors else ""
        _write(
            f"{prefix}{self.header_prefix}{self._wrap_color(node.name, header_color)}"
            f" {self._sub_text(node.desc)}{self.eol}"
        )
        if len(node.children):
            data_prefix = prefix + self.indent_with_vert + self.indent_unit
        else:
            data_prefix = prefix + self.indent_unit + self.indent_unit
        for attr in node.attrs:
            _write(
                f"{data_prefix}{self._wrap_color(attr.name, attr_color)}: {attr.value}"
            )
            if attr.display_value is not None:
                _write(f" {self._sub_text(attr.display_value)}{self.eol}")
            else:
                _write(self.eol)
        child_indent = prefix + self.indent_with_vert
        for i, child in enumerate(node.children):
            if i + 1 == len(node.children):
                child_indent = prefix + self.indent_unit
            self.show_node(child, child_indent)

    def render(self, tree: Tree):
        """Render the tree (recursive)"""
        self.show_node(tree, self.offset)

    def update_colors(self):
        """disable colours if they are not supported"""
        if not sys.stdout.isatty():
            self.disable_colors()

    def disable_colors(self):
        """Do not use ascii color prefixes and sufixes in the output"""
        self.use_colors = False
