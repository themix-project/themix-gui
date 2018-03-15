import os
from collections import defaultdict
from itertools import groupby

from .config import COLORS_DIR, USER_COLORS_DIR
from .helpers import ls_r, mkdir_p


def get_presets():
    file_paths = [
        {
            "name": "".join(
                path.startswith(COLORS_DIR) and path.rsplit(COLORS_DIR) or
                path.rsplit(USER_COLORS_DIR)
            ),
            "path": path,
            "default": is_default,
        }
        for paths, is_default in (
            (ls_r(USER_COLORS_DIR), False),
            (ls_r(COLORS_DIR), True)
        )
        for path in paths
    ]
    result = defaultdict(list)
    for _key, group in groupby(file_paths, lambda x: x['name'].split('/')[0]):
        group = sorted(list(group), key=lambda x: x['name'])
        display_name = group[0]['name']
        if display_name in result:
            display_name = display_name + " (default)"
        result[display_name] = group
    return dict(result)


def get_user_theme_path(user_theme_name):
    return os.path.join(USER_COLORS_DIR, user_theme_name)


def save_colorscheme(preset_name, colorscheme, path=None):
    colorscheme["NAME"] = preset_name
    path = path or get_user_theme_path(preset_name)
    if not os.path.exists(path):
        mkdir_p(os.path.dirname(path))
    with open(path, 'w') as file_object:
        for key, value in sorted(colorscheme.items()):
            if (
                    key not in ('NOGUI', )
            ) and (
                    not key.startswith('_')
            ) and (
                    value is not None
            ):
                file_object.write("{}={}\n".format(
                    key, value
                ))
    return path


def remove_colorscheme(preset_name):
    path = os.path.join(USER_COLORS_DIR, preset_name)
    os.remove(path)


def is_user_colorscheme(preset_path):
    return preset_path.startswith(USER_COLORS_DIR)


def is_colorscheme_exists(preset_path):
    return os.path.exists(preset_path)
