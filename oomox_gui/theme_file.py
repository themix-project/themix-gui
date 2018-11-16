import os
import shutil
from collections import defaultdict
from itertools import groupby

from .config import COLORS_DIR, USER_COLORS_DIR
from .helpers import ls_r, mkdir_p


def get_presets():
    from .plugin_loader import IMPORT_PLUGINS
    all_results = {}
    for colors_dir, is_default in [
            (COLORS_DIR, True),
            (USER_COLORS_DIR, False),
    ] + [
        (plugin.plugin_theme_dir, True)
        for plugin in IMPORT_PLUGINS.values()
        if plugin.plugin_theme_dir
    ]:
        result = defaultdict(list)
        paths = ls_r(colors_dir)
        file_paths = [
            {
                "name": "".join(
                    path.rsplit(colors_dir)
                ),
                "path": os.path.abspath(path),
                "default": is_default,
            }
            for path in paths
        ]
        for _key, group in groupby(file_paths, lambda x: x['name'].split('/')[0]):
            group = sorted(list(group), key=lambda x: x['name'])
            display_name = group[0]['name']
            # if display_name in result:
                # display_name = display_name + " (default)"
            result[display_name] = group
        all_results[colors_dir] = dict(result)
    return all_results


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


def import_colorscheme(preset_name, import_path):
    new_path = get_user_theme_path(preset_name)
    if not os.path.exists(new_path):
        mkdir_p(os.path.dirname(new_path))
    shutil.copy(import_path, new_path)
    return new_path


def remove_colorscheme(preset_name):
    path = os.path.join(USER_COLORS_DIR, preset_name)
    os.remove(path)


def is_user_colorscheme(preset_path):
    return preset_path.startswith(USER_COLORS_DIR)


def is_colorscheme_exists(preset_path):
    return os.path.exists(preset_path)
