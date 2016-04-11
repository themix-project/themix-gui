import os
import random
from gi.repository import Gdk, Gtk


script_dir = os.path.dirname(os.path.realpath(__file__))
theme_dir = os.path.join(script_dir, "../")
colors_dir = os.path.join(theme_dir, "colors/")


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


def convert_theme_color_to_gdk(theme_color):
    gdk_color = Gdk.RGBA()
    gdk_color.parse("#"+theme_color)
    return gdk_color


def read_colorscheme_from_preset(preset_name):
    colorscheme = {}
    with open(os.path.join(colors_dir, preset_name)) as f:
        for line in f.readlines():
            parsed_line = line.strip().split('=')
            # migration workaround:
            try:
                if not (
                    parsed_line[0].startswith("#") or parsed_line[0] == "NAME"
                ):
                    colorscheme[parsed_line[0]] = parsed_line[1]
            except IndexError:
                pass
    # migration workaround #2:
    for key, value in colorscheme.items():
        if value.startswith("$"):
            colorscheme[key] = colorscheme[value.lstrip("$")]
    return colorscheme


class CenterLabel(Gtk.Label):

    def __init__(self, text):
        super().__init__(text)
        self.set_justify(Gtk.Justification.CENTER)
        self.set_alignment(0.5, 0.5)
        self.set_margin_left(6)
        self.set_margin_right(6)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
