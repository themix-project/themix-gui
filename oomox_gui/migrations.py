import json
import os
from typing import TYPE_CHECKING

from .config import DEFAULT_ENCODING, USER_CONFIG_DIR

if TYPE_CHECKING:
    from typing import Any, Final

    from .plugin_api import OomoxPlugin


CONFIG_MIGRATIONS_DIR: "Final" = os.path.join(
    USER_CONFIG_DIR, "migrations/",
)


class MigrationConfig:

    DEFAULT_VERSION = 0

    def __init__(self, component_name: str) -> None:
        if not os.path.exists(CONFIG_MIGRATIONS_DIR):
            os.makedirs(CONFIG_MIGRATIONS_DIR)

        filename = f"{component_name}.json"
        self.filepath = os.path.join(CONFIG_MIGRATIONS_DIR, filename)
        try:
            with open(self.filepath, encoding=DEFAULT_ENCODING) as fobj:
                self.config = json.load(fobj)
        except Exception:
            self.config = {}
        if not self.config.get("version"):
            self.config["version"] = self.DEFAULT_VERSION

    @property
    def version(self) -> int:
        version_from_config = self.config["version"]
        if not isinstance(version_from_config, int):
            return self.DEFAULT_VERSION
        return version_from_config

    def update(self, version: int, **kwargs: "Any") -> None:
        self.config["version"] = version
        for key, value in kwargs.items():
            self.config[key] = value
        with open(self.filepath, "w", encoding=DEFAULT_ENCODING) as fobj:
            json.dump(self.config, fobj)


class PluginMigrationConfig(MigrationConfig):

    def __init__(self, plugin: "OomoxPlugin") -> None:
        super().__init__(component_name=plugin.name)
