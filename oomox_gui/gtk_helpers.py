from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from gi.repository import GdkPixbuf, Gio, GLib, Gtk
from gi.types import GObjectMeta

from .i18n import translate

if TYPE_CHECKING:
    from typing import Any

    from gi.repository import Pango


class ActionProperty(str):

    target: str
    name: str

    def __new__(cls, target: str, name: str) -> "ActionProperty":
        obj = str.__new__(cls, name)
        obj.name = name
        obj.target = target
        return obj

    def get_id(self) -> str:
        return ".".join([self.target, self.name])


class ActionsEnum(metaclass=ABCMeta):

    @property
    @abstractmethod
    def _target(self) -> str:
        pass


class CenterLabel(Gtk.Label):
    def __init__(self, label: str | None = None) -> None:
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

    def __init__(
            self,
            icon_name: str,
            tooltip_text: str | None = None,
            label: str | None = None,
    ) -> None:
        super().__init__()
        self.box = Gtk.Box()
        self.icon = Gio.ThemedIcon(name=icon_name)  # type: ignore[call-arg]
        self.image = Gtk.Image.new_from_gicon(self.icon, Gtk.IconSize.BUTTON)
        self.get_style_context().add_class("image-button")
        if label:
            self.label = Gtk.Label(label)
            self.box.pack_start(self.label, True, True, 3)
            self.get_style_context().add_class("text-button")
        self.box.pack_start(self.image, True, True, 3 if self.label else 0)
        self.add(self.box)
        if tooltip_text:
            self.set_tooltip_text(tooltip_text)


class ImageButton(Gtk.Button, ImageButtonContainer):
    def __init__(self, *args: "Any", **kwargs: "Any") -> None:
        Gtk.Button.__init__(self)
        ImageButtonContainer.__init__(self, *args, **kwargs)


class ImageMenuButton(Gtk.MenuButton, ImageButtonContainer):  # type: ignore[misc]
    def __init__(self, *args: "Any", **kwargs: "Any") -> None:
        Gtk.MenuButton.__init__(self)
        ImageButtonContainer.__init__(self, *args, **kwargs)


class ScaledImage(Gtk.Image):

    scale_factor: float
    orig_width: int | None = None
    orig_height: int | None = None
    oomox_width: int | None = None
    oomox_height: int | None = None

    def __init__(
            self,
            *args: "Any",
            width: int | None = None,
            height: int | None = None,
            **kwargs: "Any",
    ) -> None:
        super().__init__(*args, **kwargs)
        if not width or height:
            required_props_error = 'Either "width" or "height" should be set'
            raise TypeError(required_props_error)
        self._set_orig_dimensions(width=width, height=height)
        style_context = self.get_style_context()
        self.scale_factor = style_context.get_scale()

    def _set_orig_dimensions(self, width: int | None = None, height: int | None = None) -> None:
        if width:
            self.orig_width = width
        if height:
            self.orig_height = height

    def do_draw(self, cr: "Pango.Matrix") -> None:  # pylint: disable=arguments-differ
        if self.oomox_width and self.oomox_height:
            cr.scale(1 / self.scale_factor, 1 / self.scale_factor)
            cr.translate(
                self.oomox_width - self.oomox_width / self.scale_factor,
                self.oomox_height - self.oomox_height / self.scale_factor,
            )
            Gtk.Image.do_draw(self, cr)

    def do_get_preferred_width(self) -> tuple[int, int]:  # pylint: disable=arguments-differ
        if self.oomox_width:
            return self.oomox_width, self.oomox_width
        return Gtk.Image.do_get_preferred_width(self)

    def do_get_preferred_height(self) -> tuple[int, int]:  # pylint: disable=arguments-differ
        if self.oomox_height:
            return self.oomox_height, self.oomox_height
        return Gtk.Image.do_get_preferred_height(self)  # type: ignore[no-any-return]

    def set_from_bytes(
            self,
            bytes_sequence: bytes,
            width: int | None = None,
            height: int | None = None,
    ) -> None:
        self._set_orig_dimensions(width=width, height=height)
        stream = Gio.MemoryInputStream.new_from_bytes(
            GLib.Bytes.new(bytes_sequence),
        )
        self.oomox_width = self.orig_width
        self.oomox_height = self.orig_height

        # @TODO: is it possible to make it faster?
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(
            stream,
            self.oomox_width * self.scale_factor if self.oomox_width else -1,
            self.oomox_height * self.scale_factor if self.oomox_height else -1,
            True,
            None,
        )
        self.oomox_width = pixbuf.props.width // self.scale_factor
        self.oomox_height = pixbuf.props.height // self.scale_factor
        self.set_from_pixbuf(pixbuf)


class EntryDialog(Gtk.Dialog):

    entry: Gtk.Entry
    entry_text = ""

    def do_response(self, response: Gtk.ResponseType) -> None:  # pylint: disable=arguments-differ
        if response == Gtk.ResponseType.OK:
            self.entry_text = self.entry.get_text()
        self.destroy()

    def __init__(
            self,
            transient_for: Gtk.Window,
            title: str,
            text: str,
            entry_text: str | None = None,
    ) -> None:
        super().__init__(
            title=title,
            transient_for=transient_for,
            flags=0,
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

        self.add_button(translate("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(translate("_OK"), Gtk.ResponseType.OK)

        self.set_default_response(Gtk.ResponseType.OK)

        self.show_all()


class YesNoDialog(Gtk.Dialog):

    def do_response(self, _response: Gtk.ResponseType) -> None:  # pylint: disable=arguments-differ
        self.destroy()

    def __init__(
            self,
            transient_for: Gtk.Window,
            title: str = "",
            text: str | None = None,
            default_response: Gtk.ResponseType = Gtk.ResponseType.NO,
    ) -> None:
        text = text or translate("Are you sure?")
        super().__init__(
            title=title,
            transient_for=transient_for,
            flags=0,
        )
        self.set_default_size(150, 100)

        label = CenterLabel(label=text)
        box = self.get_content_area()
        box.add(label)

        self.add_button(translate("_No"), Gtk.ResponseType.NO)
        self.add_button(translate("_Yes"), Gtk.ResponseType.YES)

        self.set_default_response(default_response)

        self.show_all()


class GObjectABCMetaAbstractProperty:
    pass


class GObjectABCMeta(GObjectMeta, type):

    ABS_METHODS = "__abstract_methods__"

    def __init__(cls, name: str, transient_for: Gtk.Window, data: "Any") -> None:
        super().__init__(name, transient_for, data)  # type: ignore[arg-type]
        this_required_methods = []
        for property_name in dir(cls):
            if getattr(cls, property_name) is GObjectABCMetaAbstractProperty:
                this_required_methods.append(property_name)
                delattr(cls, property_name)
        if this_required_methods:
            setattr(
                cls, cls.ABS_METHODS,
                getattr(cls, cls.ABS_METHODS, []) + this_required_methods,
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
                missing_methods_error = (
                    f"Can't instantiate abstract class {cls.__name__}"
                    f" with abstract methods {','.join(missing_methods)}",
                )
                raise TypeError(missing_methods_error)


def g_abstractproperty(_function: "Any") -> "type[GObjectABCMetaAbstractProperty]":
    return GObjectABCMetaAbstractProperty


class _WarnOnceDialog(Gtk.MessageDialog):

    _already_shown: ClassVar[list[str]] = []

    @staticmethod
    def _marshal(text: str, secondary_text: str, buttons: Gtk.ButtonsType) -> str:
        return f"{text},{secondary_text},{buttons}"

    @classmethod
    def add_shown(cls, text: str, secondary_text: str, buttons: Gtk.ButtonsType) -> None:
        cls._already_shown.append(cls._marshal(text, secondary_text, buttons))

    @classmethod
    def was_shown(cls, text: str, secondary_text: str, buttons: Gtk.ButtonsType) -> bool:
        return cls._marshal(text, secondary_text, buttons) in cls._already_shown

    def __init__(self, text: str, secondary_text: str, buttons: Gtk.ButtonsType) -> None:
        super().__init__(
            text=text,
            secondary_text=secondary_text,
            buttons=buttons,
        )


def warn_once(
        text: str,
        secondary_text: str = "",
        buttons: Gtk.ButtonsType = Gtk.ButtonsType.CLOSE,
) -> None:
    dialog = _WarnOnceDialog(text, secondary_text, buttons)
    if dialog.was_shown(text, secondary_text, buttons):
        return
    dialog.run()
    dialog.add_shown(text, secondary_text, buttons)
    dialog.destroy()
