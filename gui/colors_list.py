from gi.repository import Gtk


class ThemeColorsList(Gtk.ScrolledWindow):

    theme = None

    def color_edited(self, widget, path, text):
        self.liststore[path][1] = text
        key = list(
            self.liststore[path]
        )[0]
        self.theme[key] = text
        self.color_edited_callback(self.theme)

    def open_theme(self, theme):
        self.liststore.clear()
        self.theme = theme
        for key, value in self.theme.items():
            self.liststore.append((key, value))

    def __init__(self, color_edited_callback):
        super().__init__()
        self.color_edited_callback = color_edited_callback
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.liststore = Gtk.ListStore(str, str)

        treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(cell_renderer=renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)
        renderer_editabletext.connect("edited", self.color_edited)
        column_editabletext = Gtk.TreeViewColumn(
            "Editable Text", renderer_editabletext, text=1
        )
        treeview.append_column(column_editabletext)

        self.add(treeview)
