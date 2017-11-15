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

