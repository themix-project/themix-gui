import os
import random
import json
from gi.repository import Gdk, Gtk, Gio

from .config import user_palette_path, FALLBACK_COLOR


def mkdir_p(dir):
    if os.path.isdir(dir):
        return
    os.makedirs(dir)


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path) for file in files[2]
    ]


def load_palette():
    try:
        with open(user_palette_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_palette(palette):
    with open(user_palette_path, 'w') as f:
        return json.dump(palette, f)


def get_random_gdk_color():
    return Gdk.RGBA(random.random(), random.random(), random.random(), 1)


def convert_theme_color_to_gdk(theme_color):
    gdk_color = Gdk.RGBA()
    gdk_color.parse("#" + theme_color)
    return gdk_color


def text_to_int(text):
    return int("0x{}".format(text), 0)


def int_to_text(myint):
    return "{0:02x}".format(int(myint))


def mix_gdk_colors(gdk_color_1, gdk_color_2, ratio):
    result_gdk_color = Gdk.RGBA()
    for attr in ('red', 'green', 'blue', 'alpha'):
        setattr(
            result_gdk_color, attr,
            (getattr(gdk_color_1, attr) * ratio + getattr(gdk_color_2, attr) *
             (1 - ratio)))
    return result_gdk_color


def mix_theme_colors(theme_color_1, theme_color_2, ratio):
    color_list_1 = []
    color_list_2 = []
    for color_text, color_list in ((theme_color_1, color_list_1),
                                   (theme_color_2, color_list_2)):
        color_list.append(color_text[:2])
        color_list.append(color_text[2:4])
        color_list.append(color_text[4:])
    result = ''
    for channel_index, channel_1_text in enumerate(color_list_1):
        try:
            channel_1 = text_to_int(channel_1_text)
            channel_2 = text_to_int(color_list_2[channel_index])
        except ValueError:
            return FALLBACK_COLOR
        result += int_to_text(channel_1 * ratio + channel_2 * (1 - ratio))
    return result


def convert_gdk_to_theme_color(gdk_color):
    return "".join([
        int_to_text(n * 255)
        for n in (gdk_color.red, gdk_color.green, gdk_color.blue)
    ])


def str_to_bool(value):
    return value.lower() == 'true'


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


class ActionsEnumValue(str):
    def __new__(cls, target, name):
        obj = str.__new__(cls, '.'.join([target, name]))
        obj.target = target
        obj.name = name
        return obj


class ActionsEnumMeta(type):
    def __init__(self, *args):
        super().__init__(*args)
        self.__target__ = object.__getattribute__(self, '__name__')

    def __getattribute__(self, attribute):
        if attribute.startswith('_'):
            return super().__getattribute__(attribute)
        target = object.__getattribute__(self, '__target__')
        name = object.__getattribute__(self, attribute)
        return ActionsEnumValue(target=target, name=name)


class ActionsEnum(metaclass=ActionsEnumMeta):
    pass
