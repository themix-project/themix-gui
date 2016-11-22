import os
import random
import subprocess
import json
from collections import defaultdict
from itertools import groupby
from gi.repository import Gdk, Gtk, Gio

from .theme_model import theme_model


script_dir = os.path.dirname(os.path.realpath(__file__))
oomox_root_dir = os.path.join(script_dir, "../")
user_config_dir = os.path.join(
    os.environ.get(
        "XDG_CONFIG_HOME",
        os.path.join(os.environ.get("HOME"), ".config/")
    ),
    "oomox/"
)
user_theme_dir = os.path.join(user_config_dir, "colors/")
colors_dir = os.path.join(oomox_root_dir, "colors/")
user_palette_path = os.path.join(user_config_dir, "recent_palette.json")

FALLBACK_COLOR = "333333"


def create_value_filter(key, value):
    def value_filter(colorscheme):
        return colorscheme[key] == value
    return value_filter


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


def load_palette():
    try:
        with open(user_palette_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_palette(palette):
    with open(user_palette_path, 'w') as f:
        return json.dump(palette, f)


def get_presets():
    file_paths = [
        {
            "name": "".join(
                path.startswith(colors_dir) and path.rsplit(colors_dir) or
                path.rsplit(user_theme_dir)
            ),
            "path": path,
        }
        for path in ls_r(user_theme_dir) + ls_r(colors_dir)
    ]
    result = defaultdict(list)
    for key, group in groupby(file_paths, lambda x: x['name'].split('/')[0]):
        group = sorted(list(group), key=lambda x: x['name'])
        display_name = group[0]['name']
        if display_name in result:
            display_name = display_name + " (default)"
        result[display_name] = group
    return dict(result)


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


def mix_theme_colors(theme_color_1, theme_color_2, ratio):
    color_list_1 = []
    color_list_2 = []
    for color_text, color_list in (
        (theme_color_1, color_list_1),
        (theme_color_2, color_list_2)
    ):
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
        result += int_to_text(
            channel_1 * ratio + channel_2 * (1 - ratio)
        )
    return result


def convert_gdk_to_theme_color(gdk_color):
    return "".join([
        int_to_text(n * 255)
        for n in (gdk_color.red, gdk_color.green, gdk_color.blue)
    ])


def str_to_bool(value):
    return value.lower() == 'true'


def bash_preprocess(preset_path):
    colorscheme = {"NOGUI": True}
    theme_values_with_keys = [
        theme_value
        for theme_value in theme_model
        if theme_value.get('key')
    ]
    process = subprocess.run(
        [
            "bash", "-c",
            "source " + preset_path + " ; " +
            "".join(
                "echo ${{{}-None}} ;".format(theme_value['key'])
                for theme_value in theme_values_with_keys
            )
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.stderr:
        raise(Exception(
            "Pre-processing failed:\nstdout:\n{}\nstderr:\n{}".format(
                process.stdout, process.stderr
            )))
    lines = process.stdout.decode("UTF-8").split()
    for i, theme_value in enumerate(theme_values_with_keys):
        value = lines[i]
        if value == 'None':
            value = None
        colorscheme[theme_value['key']] = value
    return colorscheme


def read_colorscheme_from_path(preset_path):
    # @TODO: remove legacy stuff (using bash logic inside the themes)
    colorscheme = {}
    with open(preset_path) as f:
        for line in f.readlines():
            parsed_line = line.strip().split('=')
            try:
                if not parsed_line[0].startswith("#"):
                    colorscheme[parsed_line[0]] = parsed_line[1]
            # ignore unparseable lines:
            except IndexError:
                pass

    # migration workaround:
    if colorscheme.get('NOGUI'):
        colorscheme = bash_preprocess(preset_path)

    for theme_value in theme_model:
        key = theme_value.get('key')
        if not key:
            continue
        fallback_key = theme_value.get('fallback_key')
        fallback_value = theme_value.get('fallback_value')
        value = colorscheme.get(key)
        if value is None and (fallback_key or fallback_value is not None):
            if fallback_value is not None:
                value = colorscheme[key] = fallback_value
            else:
                value = colorscheme[key] = colorscheme[fallback_key]

        if value is None:
            colorscheme[key] = FALLBACK_COLOR
        # migration workaround #2: resolve color links
        elif isinstance(value, str) and value.startswith("$"):
            try:
                colorscheme[key] = colorscheme[value.lstrip("$")]
            except KeyError:
                colorscheme[key] = FALLBACK_COLOR

        value_type = theme_value['type']
        if value_type == 'bool':
            if isinstance(value, str):
                colorscheme[key] = str_to_bool(value)
        elif value_type == 'int':
            colorscheme[key] = int(value)
        elif value_type == 'float':
            colorscheme[key] = float(value)

    return colorscheme


def read_colorscheme_from_preset(preset_name):
    return read_colorscheme_from_path(os.path.join(colors_dir, preset_name))


def save_colorscheme(preset_name, colorscheme):
    path = os.path.join(user_theme_dir, preset_name)
    try:
        with open(path, 'w') as f:
            if 'NAME' not in colorscheme:
                f.write("NAME={}\n".format(preset_name))
            for key in sorted(colorscheme.keys()):
                f.write("{}={}\n".format(
                    key, colorscheme[key]
                ))
    except FileNotFoundError:
        mkdir_p(os.path.dirname(path))
        return save_colorscheme(preset_name, colorscheme)
    return path


def remove_colorscheme(preset_name):
    path = os.path.join(user_theme_dir, preset_name)
    os.remove(path)


def is_user_colorscheme(preset_path):
    return preset_path.startswith(user_theme_dir)


def is_colorscheme_exists(preset_path):
    return os.path.exists(preset_path)


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
