from gi.repository import Gtk


class SpinnerDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Exporting...", parent, 0)

        label = Gtk.Label(
            "Please wait while\nnew colorscheme will be created"
        )
        label.set_justify(Gtk.Justification.CENTER)
        label.set_alignment(0.5, 0.5)
        label.set_margin_left(6)
        label.set_margin_right(6)
        label.set_margin_top(6)
        label.set_margin_bottom(6)

        spinner = Gtk.Spinner()
        spinner.start()

        self.log = Gtk.TextView()
        self.log.set_editable(False)
        self.log.set_cursor_visible(False)

        box = self.get_content_area()
        box.add(label)
        box.add(spinner)
        box.add(self.log)
        self.show_all()
