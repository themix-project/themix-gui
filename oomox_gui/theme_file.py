import os
import shutil
from collections import defaultdict
from itertools import groupby
from typing import TYPE_CHECKING, NamedTuple

from .config import COLORS_DIR, DEFAULT_ENCODING, USER_COLORS_DIR
from .helpers import ls_r, mkdir_p
from .plugin_api import PLUGIN_PATH_PREFIX
from .plugin_loader import PluginLoader

if TYPE_CHECKING:
    from collections.abc import Callable

    from .plugin_api import OomoxImportPlugin


ThemeValueT = str | bool | int | float | Exception
ThemeT = dict[str, ThemeValueT]


class PresetFile(NamedTuple):
    name: str
    path: str
    default: bool
    is_saveable: bool


def get_theme_name_and_plugin(
        theme_path: str,
        colors_dir: str,
        plugin: "OomoxImportPlugin | None",
) -> "tuple[str, OomoxImportPlugin | None]":
    display_name = "".join(
        theme_path.rsplit(colors_dir),
    ).lstrip("/")
    rel_path = "".join(theme_path.rsplit(colors_dir))
    if not plugin and rel_path.startswith(PLUGIN_PATH_PREFIX):
        display_name = "/".join(display_name.split("/")[1:])
        plugin_name = rel_path.split(PLUGIN_PATH_PREFIX, maxsplit=2)[1].split("/", maxsplit=1)[0]
        plugin = PluginLoader.get_import_plugins().get(plugin_name)
    if plugin:
        for ext in plugin.file_extensions:
            if display_name.endswith(ext):
                display_name = display_name[:-len(ext)]
                break
    return display_name, plugin


def get_preset_groups_sorter(colors_dir: str) -> "Callable[[PresetFile], str]":
    return lambda x: "".join(x.path.rsplit(colors_dir)).split("/", maxsplit=1)[0]


def group_presets_by_dir(
        preset_list: list[PresetFile],
        preset_dir: str,
) -> list[tuple[str, list[PresetFile]]]:
    return [
        (dir_name, list(group))
        for dir_name, group in groupby(
            preset_list,
            get_preset_groups_sorter(preset_dir),
        )
    ]


def get_presets() -> dict[str, dict[str, list[PresetFile]]]:
    all_results = {}
    for colors_dir, is_default, plugin in [
            (COLORS_DIR, True, None),
            (USER_COLORS_DIR, False, None),
    ] + [
        (import_plugin.plugin_theme_dir, True, import_plugin)
        for import_plugin in PluginLoader.get_import_plugins().values()
        if import_plugin.plugin_theme_dir
    ]:
        file_paths = []
        for path in ls_r(colors_dir):
            display_name, preset_plugin = get_theme_name_and_plugin(
                path, colors_dir, plugin,
            )
            file_paths.append(PresetFile(
                name=display_name,
                path=os.path.abspath(path),
                default=is_default or bool(preset_plugin),
                is_saveable=not is_default and not preset_plugin,
            ))
        result = defaultdict(list)
        for dir_name, group in group_presets_by_dir(file_paths, colors_dir):
            def preset_sorter(preset: PresetFile) -> str:
                return preset.name
            result[dir_name] = sorted(group, key=preset_sorter)
        all_results[colors_dir] = dict(result)
    return all_results


def get_user_theme_path(user_theme_name: str) -> str:
    return os.path.join(USER_COLORS_DIR, user_theme_name.lstrip("/"))


def save_colorscheme(preset_name: str, colorscheme: "ThemeT", path: str | None = None) -> str:
    colorscheme_to_write = {}
    colorscheme_to_write.update(colorscheme)
    colorscheme_to_write["NAME"] = f'"{preset_name}"'
    path = path or get_user_theme_path(preset_name)
    if not os.path.exists(path):
        mkdir_p(os.path.dirname(path))
    with open(path, "w", encoding=DEFAULT_ENCODING) as file_object:
        for key, value in sorted(colorscheme_to_write.items()):
            if (
                    key not in ("NOGUI", )
            ) and (
                not key.startswith("_")
            ) and (
                value is not None
            ) and (
                not isinstance(value, Exception)
            ):
                file_object.write(f"{key}={value}\n")
    return path


def import_colorscheme(preset_name: str, import_path: str) -> str:
    new_path = get_user_theme_path(preset_name)
    if not os.path.exists(new_path):
        mkdir_p(os.path.dirname(new_path))
    shutil.copy(import_path, new_path)
    return new_path


def remove_colorscheme(preset_name: str) -> None:
    path = os.path.join(USER_COLORS_DIR, preset_name)
    os.remove(path)


def is_user_colorscheme(preset_path: str) -> bool:
    return preset_path.startswith(USER_COLORS_DIR)


def is_colorscheme_exists(preset_path: str) -> bool:
    return os.path.exists(preset_path)
