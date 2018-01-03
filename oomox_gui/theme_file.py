import os
from collections import defaultdict
from itertools import groupby

from .config import colors_dir, user_theme_dir
from .helpers import ls_r, mkdir_p


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


def get_user_theme_path(user_theme_name):
    return os.path.join(user_theme_dir, user_theme_name)


def save_colorscheme(preset_name, colorscheme, path=None):
    colorscheme["NAME"] = preset_name
    path = path or get_user_theme_path(preset_name)
    if not os.path.exists(path):
        mkdir_p(os.path.dirname(path))
    with open(path, 'w') as f:
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
