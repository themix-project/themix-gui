import os
from collections import defaultdict
from itertools import groupby
import subprocess

from .config import colors_dir, user_theme_dir, FALLBACK_COLOR
from .theme_model import theme_model
from .helpers import (
    ls_r, mkdir_p,
    str_to_bool
)


def get_presets():
    file_paths = [
        {
            "name": "".join(
                path.startswith(colors_dir) and path.rsplit(colors_dir) or
                path.rsplit(user_theme_dir)
            ),
            "path": path,
            "default": is_default,
        }
        for paths, is_default in (
            (ls_r(user_theme_dir), False),
            (ls_r(colors_dir), True)
        )
        for path in paths
    ]
    result = defaultdict(list)
    for key, group in groupby(file_paths, lambda x: x['name'].split('/')[0]):
        group = sorted(list(group), key=lambda x: x['name'])
        display_name = group[0]['name']
        if display_name in result:
            display_name = display_name + " (default)"
        result[display_name] = group
    return dict(result)


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

        if value is None and fallback_value is False:
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


def get_user_theme_path(user_theme_name):
    return os.path.join(user_theme_dir, user_theme_name)


def save_colorscheme(preset_name, colorscheme):
    path = get_user_theme_path(preset_name)
    if not os.path.exists(path):
        mkdir_p(os.path.dirname(path))
    with open(path, 'w') as f:
        if 'NAME' not in colorscheme:
            f.write("NAME={}\n".format(preset_name))
        for key in sorted(colorscheme.keys()):
            if key not in ('NOGUI'):
                f.write("{}={}\n".format(
                    key, colorscheme[key]
                ))
    return path


def remove_colorscheme(preset_name):
    path = os.path.join(user_theme_dir, preset_name)
    os.remove(path)


def is_user_colorscheme(preset_path):
    return preset_path.startswith(user_theme_dir)


def is_colorscheme_exists(preset_path):
    return os.path.exists(preset_path)
