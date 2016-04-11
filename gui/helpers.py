import os
import random
import subprocess
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

THEME_KEYS = [
    'BG',
    'FG',
    'MENU_BG',
    'MENU_FG',
    'SEL_BG',
    'SEL_FG',
    'TXT_BG',
    'TXT_FG',
    'BTN_BG',
    'BTN_FG',
]


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


def resolve_color_links(colorscheme):
    # @TODO: remove it
    for key, value in colorscheme.items():
        if value.startswith("$"):
            try:
                colorscheme[key] = colorscheme[value.lstrip("$")]
            except KeyError:
                colorscheme[key] = "ff3333"
    return colorscheme


def bash_preprocess(preset_path):
    colorscheme = {"NOGUI": True}
    lines = subprocess.run(
        [
            "bash", "-c",
            "source " + preset_path + " ; " +
            "".join("echo ${} ;".format(key) for key in THEME_KEYS)
        ],
        stdout=subprocess.PIPE
    ).stdout.decode("UTF-8").split()

    i = 0
    for key in THEME_KEYS:
        colorscheme[key] = lines[i]
        i += 1

    return colorscheme


def read_colorscheme_from_path(preset_path):
    # @TODO: remove legacy stuff
    colorscheme = {}
    with open(preset_path) as f:
        for line in f.readlines():
            parsed_line = line.strip().split('=')
            # migration workaround:
            try:
                if not parsed_line[0].startswith("#"):
                    colorscheme[parsed_line[0]] = parsed_line[1]
            except IndexError:
                pass
    # migration workaround #2:
    if 'NOGUI' in colorscheme:
        colorscheme = bash_preprocess(preset_path)
    else:
        colorscheme = resolve_color_links(colorscheme)
    return colorscheme


def read_colorscheme_from_preset(preset_name):
    return read_colorscheme_from_path(os.path.join(colors_dir, preset_name))


def save_colorscheme(preset_name, colorscheme):
    path = os.path.join(user_theme_dir, preset_name)
    with open(path, 'w') as f:
        f.write("NAME={}\n".format(preset_name))
        for key in THEME_KEYS:
            f.write("{}={}\n".format(key, colorscheme[key]))
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
