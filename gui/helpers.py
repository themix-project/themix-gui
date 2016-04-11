import os
import random
from gi.repository import Gdk, Gtk, Gio


script_dir = os.path.dirname(os.path.realpath(__file__))
theme_dir = os.path.join(script_dir, "../")
user_theme_dir = os.path.join(
    os.environ.get(
        "XDG_CONFIG_HOME",
        os.path.join(os.environ.get("HOME"), ".config/")
    ),
    "oomox/"
)
colors_dir = os.path.join(theme_dir, "colors/")


def mkdir_p(dir):
    if os.path.isdir(dir):
        return
    os.makedirs(dir)


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path)
        for file in files[2]
    ]


def get_presets():
    result = {
        "".join(
            path.startswith(colors_dir) and path.rsplit(colors_dir) or
            path.rsplit(user_theme_dir)
        ): path
        for path in ls_r(colors_dir) + ls_r(user_theme_dir)
    }
    return result


def get_random_gdk_color():
    return Gdk.RGBA(random.random(), random.random(), random.random(), 1)


def convert_theme_color_to_gdk(theme_color):
    gdk_color = Gdk.RGBA()
    gdk_color.parse("#" + theme_color)
    return gdk_color


def read_colorscheme_from_path(preset_path):
    colorscheme = {}
    with open(preset_path) as f:
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


def read_colorscheme_from_preset(preset_name):
    return read_colorscheme_from_path(os.path.join(colors_dir, preset_name))


def save_colorscheme(preset_name, colorscheme):
    path = os.path.join(user_theme_dir, preset_name)
    with open(path, 'w') as f:
        f.write("NAME={}\n".format(preset_name))
        for key, value in colorscheme.items():
            f.write("{}={}\n".format(key, value))
    return path


class CenterLabel(Gtk.Label):

    def __init__(self, text):
        super().__init__(text)
        self.set_justify(Gtk.Justification.CENTER)
        self.set_alignment(0.5, 0.5)
        self.set_margin_left(6)
        self.set_margin_right(6)
        self.set_margin_top(6)
        self.set_margin_bottom(6)


class ImageButton(Gtk.Button):

    icon = None
    image = None

    def __init__(self, icon_name, tooltip_text=None):
        super().__init__()
        self.icon = Gio.ThemedIcon(name=icon_name)
        self.image = Gtk.Image.new_from_gicon(self.icon, Gtk.IconSize.BUTTON)
        self.add(self.image)
        if tooltip_text:
            self.set_tooltip_text(tooltip_text)
