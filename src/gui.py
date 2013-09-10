#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk


class GtkRenderer(object):
    def __init__(self):
        w = gtk.Window()
        w.resize(1024, 768)
        w.connect("delete_event", self.on_delete)
        w.connect("destroy", self.on_destroy)
        self.window = w

    def on_delete(self, widget, event, data=None):
        return False

    def on_destroy(self, widget, data=None):
        gtk.main_quit()

    def populate(self, datanode, parent=None):
        treenode = self.treestore.append(parent, [datanode.name])
        for attr in datanode.attrs:
            self.treestore.append(treenode, ["%s: %s" %(
                attr.name, attr.display_value if attr.display_value else attr.value)])
        for child in datanode.children:
            self.populate(child, treenode)

    def render(self, data):
        self.treestore = gtk.TreeStore(str)
        self.treeview = gtk.TreeView(self.treestore)

        col = gtk.TreeViewColumn(data.name)
        self.treeview.append_column(col)
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', 0)

        for child in data.children:
            self.populate(child)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.treeview)
        self.window.add(sw)
        self.treeview.expand_all()
        self.window.show_all()
        gtk.main()

