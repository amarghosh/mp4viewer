
class Attr(object):
    def __init__(self, name, value, display_value=None):
        if type(name) is not str:
            raise Exception("name should be string")
        self.name = name
        self.value = value
        self.display_value = display_value

class Tree(object):
    def __init__(self, name):
        self.name = name
        self.attrs = []
        self.children = []

    # First arg can be Attr or the name. If it is name, give value and optional converted value
    def add_attr(self, *args):
        if len(args) == 0:
            raise Exception("Add what?")
        if len(args) == 1 and type(args[0]) is Attr:
            self.attrs.append(args[0])
        elif len(args) == 1:
            raise Exception("Sole argument should be an Attr, received %s" %type(args[0]))
        else:
            self.attrs.append(Attr(args[0], args[1], args[2] if len(args) > 2 else None))

    def add_child(self, child):
        if type(child) is not Tree:
            child = Tree(child)
        self.children.append(child)
        return child

    def __str__(self):
        return self.name
