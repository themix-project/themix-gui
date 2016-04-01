from gi.repository import Gtk


class SpinnerDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Exporting...", parent, 0)

        label = Gtk.Label("Please wait while new colorscheme will be created")
        spinner = Gtk.Spinner()
        spinner.start()

        box = self.get_content_area()
        box.add(label)
        box.add(spinner)
        self.show_all()
