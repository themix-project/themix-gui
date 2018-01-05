from gi.repository import Gtk, Gio
from gi.types import GObjectMeta


class CenterLabel(Gtk.Label):
    def __init__(self, text=None):
        super().__init__()
        if text:
            self.set_text(text)
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

    def do_response(self, response):  # pylint: disable=arguments-differ
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


class YesNoDialog(Gtk.Dialog):

    def do_response(self, _response):  # pylint: disable=arguments-differ
        self.destroy()

    def __init__(self, parent,
                 title="",
                 text=_("Are you sure?"),
                 default_response=Gtk.ResponseType.NO):
        Gtk.Dialog.__init__(self, title, parent, 0)
        self.set_default_size(150, 100)

        label = CenterLabel(text)
        box = self.get_content_area()
        box.add(label)

        self.add_button(_("_No"), Gtk.ResponseType.NO)
        self.add_button(_("_Yes"), Gtk.ResponseType.YES)

        self.set_default_response(default_response)

        self.show_all()


class GObjectABCMetaAbstractProperty():
    pass


class GObjectABCMeta(GObjectMeta):

    ABS_METHODS = '__abstract_methods__'

    def __init__(cls, name, parents, data):
        super().__init__(name, parents, data)
        for property_name in dir(cls):
            if getattr(cls, property_name) is GObjectABCMetaAbstractProperty:
                setattr(
                    cls, cls.ABS_METHODS,
                    getattr(cls, cls.ABS_METHODS, []) + [property_name]
                )
                delattr(cls, property_name)
        if not (getattr(cls, cls.ABS_METHODS) and not any(
                cls.ABS_METHODS in B.__dict__ for B in cls.__mro__[1:]
        )):
            required_methods = getattr(cls, cls.ABS_METHODS)
            for method_name in required_methods:
                if any(method_name in B.__dict__ for B in cls.__mro__):
                    return
            raise TypeError(
                "Can't instantiate abstract class {} with abstract methods {}".format(
                    cls.__name__,
                    ','.join(required_methods)
                )
            )


def g_abstractproperty(_function):
    return GObjectABCMetaAbstractProperty
