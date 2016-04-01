import os
import random
from gi.repository import Gdk


script_dir = os.path.dirname(os.path.realpath(__file__))
colors_dir = os.path.join(script_dir, "../colors/")


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path)
        for file in files[2]
    ]


def get_presets():
    result = {
        "".join(path.rsplit(colors_dir)): path
        for path in ls_r(colors_dir)
    }
    return result


def get_random_gdk_color():
    return Gdk.RGBA(random.random(), random.random(), random.random(), 1)


def hex_str_to_float(s):
    return int("0x{}".format(s), 16)/255


def convert_theme_color_to_gdk(theme_color):
    r = hex_str_to_float(theme_color[:2])
    g = hex_str_to_float(theme_color[2:4])
    b = hex_str_to_float(theme_color[4:])
    return Gdk.RGBA(r, g, b, 1)


def read_colorscheme_from_preset(preset_name):
    colorscheme = {}
    with open(os.path.join(colors_dir, preset_name)) as f:
        for line in f.readlines():
            parsed_line = line.strip().split('=')
            # migration workaround:
            try:
                if parsed_line[0] != "NAME":
                    colorscheme[parsed_line[0]] = parsed_line[1]
            except IndexError:
                pass
    # migration workaround #2:
    for key, value in colorscheme.items():
        if value.startswith("$"):
            colorscheme[key] = colorscheme[value.lstrip("$")]
    return colorscheme
