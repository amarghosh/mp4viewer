""" json renderer """

import os
import json


class JsonRenderer:
    """json renderer"""

    def __init__(self, mp4_path, output_path):
        self.mp4_path = mp4_path
        if output_path is not None:
            self.output_path = output_path
        else:
            mp4_base_name = os.path.basename(mp4_path)
            self.output_path = f"./{mp4_base_name}.mp4viewer.json"

    def _write(self, output_object):
        print(self.output_path)
        with open(self.output_path, "w+", encoding="utf-8") as fd:
            fd.write(json.dumps(output_object, indent=2))

    def render(self, data):
        """generate a json object from the mp4 metadata"""
        root = {"file": self.mp4_path}
        for child in data.children:
            self.add_node(child, root)
        self._write(root)

    def add_node(self, node, parent):
        """recursively serialise box data"""
        if "children" not in parent:
            parent["children"] = []
        j_node = {}
        j_node["boxtype"] = {"fourcc": node.name, "description": node.desc}
        parent["children"].append(j_node)
        for attr in node.attrs:
            if attr.display_value is not None:
                j_node[attr.name] = {
                    "raw value": attr.value,
                    "decoded": attr.display_value,
                }
            else:
                j_node[attr.name] = attr.value
        for child in node.children:
            self.add_node(child, j_node)
        return j_node
