""" Defines the tree model used to represent the boxes """

from dataclasses import dataclass


@dataclass
class Attr:
    """An attribute of the tree"""

    def __init__(self, name: str, value, display_value=None):
        if not isinstance(name, str):
            raise TypeError("name should be string")
        self.name = name
        self.value = value
        self.display_value = display_value


class Tree:
    """Class representing a Tree"""

    TREE_TYPE_ATOM = 0
    TREE_TYPE_DICT = 1

    def __init__(self, name, desc=None, tree_type=TREE_TYPE_ATOM):
        self.name = name
        self.desc = desc
        self.tree_type = tree_type
        self.attrs = []
        self.children = []

    def is_atom(self):
        """Return true if this tree represents an ISO box"""
        return self.tree_type == Tree.TREE_TYPE_ATOM

    def add_attr(self, *args):
        """Add an attribute to the root node of this tree"""
        # First arg can be Attr or the name. If it is name, give value and optional converted value
        if len(args) == 0:
            raise TypeError("Add what?")
        if len(args) == 1 and isinstance(args[0], Attr):
            self.attrs.append(args[0])
        elif len(args) == 1:
            raise TypeError(
                f"Sole argument should be an Attr, received {type(args[0])}"
            )
        else:
            self.attrs.append(
                Attr(args[0], args[1], args[2] if len(args) > 2 else None)
            )

    def add_child(self, child):
        """Add a child node to this tree"""
        if not isinstance(child, Tree):
            child = Tree(child)
        self.children.append(child)
        return child

    def __str__(self):
        return f"Tree<{self.name}>"
