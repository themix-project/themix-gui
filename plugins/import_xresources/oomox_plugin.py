import os
import subprocess

from oomox_gui.plugin_api import OomoxImportPlugin


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


class XrdbCache():

    _cache = None

    @classmethod
    def get(cls):
        if cls._cache:
            return cls._cache

        timeout = 10
        command = ['xrdb', '-query']

        result = {}
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for line in iter(proc.stdout.readline, b''):
            line = line.decode("utf-8")
            key, value, *_rest = line.split(':')
            key = key.lstrip('*').lstrip('.')
            value = value.strip()
            result[key] = value
        proc.communicate(timeout=timeout)
        if proc.returncode == 0:
            cls._cache = result
            return result
        print('xrdb not found')
        return None

    @classmethod
    def clear(cls):
        cls._cache = None


class Plugin(OomoxImportPlugin):

    name = 'import_xresources'
    display_name = 'Xresources'
    plugin_theme_dir = os.path.abspath(
        os.path.join(PLUGIN_DIR, 'colors')
    )

    # theme_model_import = []

    def read_colorscheme_from_path(self, preset_path):
        # pylint:disable=bad-option-value,import-outside-toplevel
        from oomox_gui.theme_model import THEME_MODEL

        theme_keys = [
            item['key']
            for section in THEME_MODEL.values()
            for item in section
            if 'key' in item
        ]

        colorscheme = {}

        with open(preset_path) as file_object:
            for line in file_object.readlines():
                key, _sep, value = line.strip().partition('=')
                if key.startswith("#") or key not in theme_keys:
                    continue
                if value.startswith('xrdb.'):
                    xrdb_color = XrdbCache.get().get(value.replace('xrdb.', ''))
                    if xrdb_color and xrdb_color.startswith('#'):
                        value = xrdb_color.replace('#', '')
                colorscheme[key] = value

        XrdbCache.clear()
        return colorscheme
