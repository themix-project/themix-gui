import os
import random
from enum import Enum

from gi.repository import Gdk

from .config import FALLBACK_COLOR


def mkdir_p(path):
    if os.path.isdir(path):
        return
    os.makedirs(path)


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path, followlinks=True) for file in files[2]
    ]


def hex_to_int(text):
    return int("0x{}".format(text), 0)


def int_to_hex(myint):
    return "{0:02x}".format(int(myint))


def convert_theme_color_to_gdk(theme_color):
    gdk_color = Gdk.RGBA()
    gdk_color.parse("#" + theme_color)
    return gdk_color


def convert_gdk_to_theme_color(gdk_color):
    return "".join([
        int_to_hex(n * 255)
        for n in (gdk_color.red, gdk_color.green, gdk_color.blue)
    ])


def get_random_gdk_color():
    return Gdk.RGBA(random.random(), random.random(), random.random(), 1)


def get_random_theme_color():
    return convert_gdk_to_theme_color(get_random_gdk_color())


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
            channel_1 = hex_to_int(channel_1_text)
            channel_2 = hex_to_int(color_list_2[channel_index])
        except ValueError:
            return FALLBACK_COLOR
        result += int_to_hex(channel_1 * ratio + channel_2 * (1 - ratio))
    return result


def str_to_bool(value):
    return value.lower() == 'true'


class ActionsEnum(Enum):

    def get_name(self):
        return self.name

    def get_id(self):
        return '.'.join([self._target.value, self.name])
