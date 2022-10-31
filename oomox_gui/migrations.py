import json
import os

from .config import USER_CONFIG_DIR, DEFAULT_ENCODING
from .plugin_api import OomoxPlugin


CONFIG_MIGRATIONS_DIR = os.path.join(
    USER_CONFIG_DIR, "migrations/"
)


class MigrationConfig:

    def __init__(self, component_name):
        if not os.path.exists(CONFIG_MIGRATIONS_DIR):
            os.makedirs(CONFIG_MIGRATIONS_DIR)

        filename = f'{component_name}.json'
        self.filepath = os.path.join(CONFIG_MIGRATIONS_DIR, filename)
        try:
            with open(self.filepath, encoding=DEFAULT_ENCODING) as fobj:
                self.config = json.load(fobj)
        except Exception:
            self.config = {}
        if not self.config.get('version'):
            self.config['version'] = 0

    @property
    def version(self) -> int:
        return self.config['version']

    def update(self, version: int, **kwargs) -> None:
        self.config['version'] = version
        for key, value in kwargs.items():
            self.config[key] = value
        with open(self.filepath, 'w', encoding=DEFAULT_ENCODING) as fobj:
            json.dump(self.config, fobj)


class PluginMigrationConfig(MigrationConfig):

    def __init__(self, plugin: OomoxPlugin):
        super().__init__(component_name=plugin.name)
