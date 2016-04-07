from gi.repository import Gtk


class CenterLabel(Gtk.Label):

    def __init__(self, text):
        super().__init__(text)
        self.set_justify(Gtk.Justification.CENTER)
        self.set_alignment(0.5, 0.5)
        self.set_margin_left(6)
        self.set_margin_right(6)
        self.set_margin_top(6)
        self.set_margin_bottom(6)


class SpinnerDialog(Gtk.Dialog):

    def _close_button_callback(self, widget):
        self.destroy()

    def show_error(self):
        self.label.destroy()
        self.spinner.destroy()

        label = CenterLabel(
            "Something went wrong :("
        )
        label.set_alignment(0.5, 0.5)


        button = Gtk.Button(label="Dismiss")
        button.connect("clicked", self._close_button_callback)

        self.box.add(label)
        self.box.add(button)
        self.show_all()


    def set_text(self, text):
        self.log.get_buffer().set_text(text)

    def _resize_callback(self, widget, event, data=None):
        adj = self.scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Exporting...", parent, 0)
        self.set_default_size(150, 150)

        self.label = CenterLabel(
            "Please wait while\nnew colorscheme will be created"
        )

        self.spinner = Gtk.Spinner()
        self.spinner.start()

        self.log = Gtk.TextView()
        self.log.set_editable(False)
        #self.log.set_cursor_visible(False)
        self.log.set_monospace(True)
        self.log.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.log.connect('size-allocate', self._resize_callback)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.log)
        self.scrolled_window.set_min_content_height(100)

        self.box = self.get_content_area()
        self.box.add(self.label)
        self.box.add(self.spinner)
        self.box.add(self.scrolled_window)
        self.show_all()
