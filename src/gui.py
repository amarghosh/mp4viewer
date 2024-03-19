""" GTK based renderer """
# pylint: disable=import-error,wrong-import-position
import xml.etree.ElementTree as ET
import gi
from gi.repository import Gtk
gi.require_version("Gtk", "3.0")

class GtkRenderer:
    """ GTK based renderer """
    def __init__(self):
        w = Gtk.Window()
        w.resize(1024, 768)
        w.connect("delete_event", self.on_delete)
        w.connect("destroy", self.on_destroy)
        self.window = w
        self.treestore = None
        self.treeview = None

    def on_delete(self, widget, event, data=None):
        # pylint: disable=unused-argument,missing-function-docstring
        return False

    def on_destroy(self, widget, data=None):
        # pylint: disable=unused-argument,missing-function-docstring
        Gtk.main_quit()

    def format_node(self, name, value, istitle=False):
        """ Returns an xml string that describes a single row """
        root = ET.Element('markup')
        color = 'red' if istitle else 'blue'
        child = ET.SubElement(root, 'span', {'foreground' : color})
        child.text = name
        child = ET.SubElement(root, 'span', {'foreground' : 'black'})
        child.text = f": {value}"
        return ET.tostring(root).decode()

    def populate(self, datanode, parent=None):
        """ Add entries for each attribute of the current node and its children (recursive) """
        treenode = self.treestore.append(parent, [
            self.format_node(datanode.name, datanode.desc, True)
        ])
        for attr in datanode.attrs:
            self.treestore.append(treenode, [self.format_node(
                attr.name, attr.display_value if attr.display_value else attr.value
            )])
        for child in datanode.children:
            self.populate(child, treenode)

    def render(self, data):
        """ render the tree """
        self.treestore = Gtk.TreeStore(str)
        self.treeview = Gtk.TreeView(model=self.treestore)

        col = Gtk.TreeViewColumn(data.name)
        cell = Gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, "markup", 0)
        self.treeview.append_column(col)

        for child in data.children:
            self.populate(child)

        sw = Gtk.ScrolledWindow()
        sw.set_vexpand(True)
        sw.add(self.treeview)
        self.window.add(sw)
        self.treeview.expand_all()
        self.window.show_all()
        Gtk.main()
