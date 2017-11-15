from gi.repository import Gtk, Gio


class CenterLabel(Gtk.Label):
    def __init__(self, text):
        super().__init__(text)
        self.set_justify(Gtk.Justification.CENTER)
        self.set_alignment(0.5, 0.5)
        self.set_margin_left(6)
        self.set_margin_right(6)
        self.set_margin_top(6)
        self.set_margin_bottom(6)


class ImageContainer(Gtk.Container):
    icon = None
    image = None

    def __init__(self, icon_name, tooltip_text=None):
        super().__init__()
        self.icon = Gio.ThemedIcon(name=icon_name)
        self.image = Gtk.Image.new_from_gicon(self.icon, Gtk.IconSize.BUTTON)
        self.add(self.image)
        if tooltip_text:
            self.set_tooltip_text(tooltip_text)


class ImageButton(Gtk.Button, ImageContainer):
    def __init__(self, *args, **kwargs):
        Gtk.Button.__init__(self)
        ImageContainer.__init__(self, *args, **kwargs)


class ImageMenuButton(Gtk.MenuButton, ImageContainer):
    def __init__(self, *args, **kwargs):
        Gtk.MenuButton.__init__(self)
        ImageContainer.__init__(self, *args, **kwargs)


class EntryDialog(Gtk.Dialog):

    entry = None
    entry_text = ''

    def do_response(self, response):
        if response == Gtk.ResponseType.OK:
            self.entry_text = self.entry.get_text()
        self.destroy()

    def __init__(
        self, parent,
        title, text, entry_text=None
    ):
        Gtk.Dialog.__init__(self, title, parent, 0)

        self.set_default_size(150, 100)

        label = Gtk.Label(text)
        self.entry = Gtk.Entry()
        self.entry.set_activates_default(True)
        if entry_text:
            self.entry.set_text(entry_text)

        box = self.get_content_area()
        box.add(label)
        box.add(self.entry)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)

        self.set_default_response(Gtk.ResponseType.OK)

        self.show_all()
