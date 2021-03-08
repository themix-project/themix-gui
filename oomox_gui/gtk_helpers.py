from abc import ABCMeta, abstractproperty

from gi.repository import Gtk, Gio, GLib, GdkPixbuf
from gi.types import GObjectMeta

from .i18n import _


class ActionProperty(str):

    target = None  # type: str
    name = None  # type: str

    def __new__(cls, name: str, target: str) -> 'ActionProperty':
        obj = str.__new__(cls, name)
        obj.name = name
        obj.target = target
        return obj

    def get_id(self) -> str:
        return '.'.join([self.target, self.name])


class ActionsABC(ABCMeta):

    def __getattribute__(cls, item: str) -> ActionProperty:
        if item.startswith('_') or item not in dir(cls):
            return ABCMeta.__getattribute__(cls, item)
        return ActionProperty(name=item, target=cls._target)


class ActionsEnum(metaclass=ActionsABC):

    @abstractproperty
    def _target(self) -> str:
        pass


class CenterLabel(Gtk.Label):
    def __init__(self, label=None):
        super().__init__()
        if label:
            self.set_text(label)
        self.set_justify(Gtk.Justification.CENTER)
        self.set_alignment(0.5, 0.5)
        self.set_margin_left(6)
        self.set_margin_right(6)
        self.set_margin_top(6)
        self.set_margin_bottom(6)


class ImageButtonContainer(Gtk.Box):
    box = None
    label = None
    icon = None
    image = None

    def __init__(self, icon_name, tooltip_text=None, label=None):
        super().__init__()
        self.box = Gtk.Box()
        self.icon = Gio.ThemedIcon(name=icon_name)
        self.image = Gtk.Image.new_from_gicon(self.icon, Gtk.IconSize.BUTTON)
        self.get_style_context().add_class('image-button')
        if label:
            self.label = Gtk.Label(label)
            self.box.pack_start(self.label, True, True, 3)
            self.get_style_context().add_class('text-button')
        self.box.pack_start(self.image, True, True, 3 if self.label else 0)
        self.add(self.box)
        if tooltip_text:
            self.set_tooltip_text(tooltip_text)


class ImageButton(Gtk.Button, ImageButtonContainer):
    def __init__(self, *args, **kwargs):
        Gtk.Button.__init__(self)
        ImageButtonContainer.__init__(self, *args, **kwargs)


class ImageMenuButton(Gtk.MenuButton, ImageButtonContainer):
    def __init__(self, *args, **kwargs):
        Gtk.MenuButton.__init__(self)
        ImageButtonContainer.__init__(self, *args, **kwargs)


class ScaledImage(Gtk.Image):

    scale_factor = None
    orig_width = None
    orig_height = None
    oomox_width = None
    oomox_height = None

    def __init__(self, *args, width=None, height=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not width or height:
            raise TypeError('Either "width" or "height" should be set')
        self._set_orig_dimensions(width=width, height=height)
        style_context = self.get_style_context()
        self.scale_factor = style_context.get_scale()

    def _set_orig_dimensions(self, width=None, height=None):
        if width:
            self.orig_width = width
        if height:
            self.orig_height = height

    def do_draw(self, cr):  # pylint: disable=arguments-differ
        if self.oomox_width:
            cr.scale(1/self.scale_factor, 1/self.scale_factor)
            cr.translate(
                self.oomox_width - self.oomox_width/self.scale_factor,
                self.oomox_height - self.oomox_height/self.scale_factor
            )
            Gtk.Image.do_draw(self, cr)

    def do_get_preferred_width(self):  # pylint: disable=arguments-differ
        if self.oomox_width:
            return self.oomox_width, self.oomox_width
        return Gtk.Image.do_get_preferred_width(self)

    def do_get_preferred_height(self):  # pylint: disable=arguments-differ
        if self.oomox_height:
            return self.oomox_height, self.oomox_height
        return Gtk.Image.do_get_preferred_height(self)

    def set_from_bytes(self, bytes_sequence, width=None, height=None):
        self._set_orig_dimensions(width=width, height=height)
        stream = Gio.MemoryInputStream.new_from_bytes(
            GLib.Bytes.new(bytes_sequence)
        )
        self.oomox_width = self.orig_width
        self.oomox_height = self.orig_height

        # @TODO: is it possible to make it faster?
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(
            stream,
            self.oomox_width*self.scale_factor if self.oomox_width else -1,
            self.oomox_height*self.scale_factor if self.oomox_height else -1,
            True,
            None
        )
        self.oomox_width = pixbuf.props.width // self.scale_factor
        self.oomox_height = pixbuf.props.height // self.scale_factor
        self.set_from_pixbuf(pixbuf)


class EntryDialog(Gtk.Dialog):

    entry = None
    entry_text = ''

    def do_response(self, response):  # pylint: disable=arguments-differ
        if response == Gtk.ResponseType.OK:
            self.entry_text = self.entry.get_text()
        self.destroy()

    def __init__(
            self, transient_for,
            title, text, entry_text=None
    ):
        super().__init__(
            title=title,
            transient_for=transient_for,
            flags=0
        )

        self.set_default_size(150, 100)

        label = Gtk.Label(label=text)
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

    def __init__(self, transient_for,
                 title="",
                 text=_("Are you sure?"),
                 default_response=Gtk.ResponseType.NO):
        super().__init__(
            title=title,
            transient_for=transient_for,
            flags=0
        )
        self.set_default_size(150, 100)

        label = CenterLabel(label=text)
        box = self.get_content_area()
        box.add(label)

        self.add_button(_("_No"), Gtk.ResponseType.NO)
        self.add_button(_("_Yes"), Gtk.ResponseType.YES)

        self.set_default_response(default_response)

        self.show_all()


class GObjectABCMetaAbstractProperty():
    pass


class GObjectABCMeta(GObjectMeta, type):

    ABS_METHODS = '__abstract_methods__'

    def __init__(cls, name, transient_fors, data):
        super().__init__(name, transient_fors, data)
        this_required_methods = []
        for property_name in dir(cls):
            if getattr(cls, property_name) is GObjectABCMetaAbstractProperty:
                this_required_methods.append(property_name)
                delattr(cls, property_name)
        if this_required_methods:
            setattr(
                cls, cls.ABS_METHODS,
                getattr(cls, cls.ABS_METHODS, []) + this_required_methods
            )

        if not (
                getattr(cls, cls.ABS_METHODS, None) and not any(
                    cls.ABS_METHODS in B.__dict__ for B in cls.__mro__[1:]
                )
        ):
            required_methods = getattr(cls, cls.ABS_METHODS, [])
            missing_methods = []
            for method_name in required_methods:
                if (
                        not any(method_name in B.__dict__ for B in cls.__mro__)
                ) and (
                    method_name not in this_required_methods
                ):
                    missing_methods.append(method_name)
            if missing_methods:
                raise TypeError(
                    "Can't instantiate abstract class {} with abstract methods {}".format(
                        cls.__name__,
                        ','.join(missing_methods)
                    )
                )


def g_abstractproperty(_function):
    return GObjectABCMetaAbstractProperty
