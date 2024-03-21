""" json renderer """

import json

class JsonRenderer:
    """ json renderer """
    def render(self, data):
        """ generate a json object from the mp4 metadata """
        root = { 'file': data.name }
        for child in data.children:
            self.add_node(child, root)
        print(json.dumps(root, indent=2))

    def add_node(self, node, parent):
        """ recursively serialise box data """
        if 'children' not in parent:
            parent['children'] = []
        j_node = {}
        j_node['boxtype'] = { 'fourcc': node.name, 'description': node.desc }
        parent['children'].append(j_node)
        for attr in node.attrs:
            if attr.display_value is not None:
                j_node[attr.name] = { 'raw value': attr.value, 'decoded': attr.display_value }
            else:
                j_node[attr.name] = attr.value
        for child in node.children:
            self.add_node(child, j_node)
        return j_node
