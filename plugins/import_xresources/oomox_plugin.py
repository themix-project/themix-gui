import os
import subprocess

from oomox_gui.config import DEFAULT_ENCODING
from oomox_gui.plugin_api import OomoxImportPlugin
from oomox_gui.theme_model import get_theme_model

PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


class XrdbCache:

    _cache: dict[str, str] | None = None

    @classmethod
    def get(cls) -> dict[str, str] | None:
        if cls._cache:
            return cls._cache

        timeout = 10
        command = ["xrdb", "-query"]

        result = {}
        with subprocess.Popen(
            command,  # noqa: S603
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as proc:
            for byte_line in iter(proc.stdout.readline, b""):
                line = byte_line.decode(DEFAULT_ENCODING)
                key, value, *_rest = line.split(":")
                key = key.lstrip("*").lstrip(".")
                value = value.strip()
                result[key] = value
            proc.communicate(timeout=timeout)
            if proc.returncode == 0:
                cls._cache = result
                return result
        print("xrdb not found")
        return None

    @classmethod
    def clear(cls) -> None:
        cls._cache = None


class Plugin(OomoxImportPlugin):

    name = "import_xresources"
    display_name = "Xresources"
    plugin_theme_dir = os.path.abspath(
        os.path.join(PLUGIN_DIR, "colors"),
    )

    # theme_model_import = []

    def read_colorscheme_from_path(self, preset_path: str) -> dict[str, str]:

        theme_keys = [
            item["key"]
            for section in get_theme_model().values()
            for item in section
            if "key" in item
        ]

        colorscheme = {}

        with open(preset_path, encoding=DEFAULT_ENCODING) as file_object:
            for line in file_object.readlines():
                key, _sep, value = line.strip().partition("=")
                if key.startswith("#") or key not in theme_keys:
                    continue
                if value.startswith("xrdb."):
                    xrdb_color = XrdbCache.get().get(value.replace("xrdb.", ""))
                    if xrdb_color and xrdb_color.startswith("#"):
                        value = xrdb_color.replace("#", "")
                colorscheme[key] = value

        XrdbCache.clear()
        return colorscheme
