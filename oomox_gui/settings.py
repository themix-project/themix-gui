import os
import json
from typing import Any

from .i18n import translate
from .config import USER_CONFIG_DIR, DEFAULT_ENCODING


class CommonOomoxConfig:

    name: str
    config_dir: str
    config_path: str
    default_config: dict[str, str]
    config: dict[str, Any]

    def __init__(self, config_dir, config_name, default_config=None):
        self.name = config_name
        self.config_dir = config_dir
        self.config_path = os.path.join(
            self.config_dir,
            f"{self.name}.json"
        )
        self.default_config = default_config or {}
        self.config = self.default_config or {}
        self.load()

    def __str__(self):
        return str(self.config)

    def __repr__(self):
        return f"Config<{str(self)}>"

    def load(self):
        try:
            with open(self.config_path, 'r', encoding=DEFAULT_ENCODING) as file_object:
                for key, value in json.load(file_object).items():
                    self.config[key] = value
        except Exception as exc:
            print(translate("Can't read config file"))
            print(exc)
        return self.config

    def save(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        with open(self.config_path, 'w', encoding=DEFAULT_ENCODING) as file_object:
            return json.dump(self.config, file_object)

    def get(self, item, fallback=None):
        return self.config.get(item, fallback)

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = value

    @property
    def _public_members(self):
        return dir(self) + list(self.__annotations__.keys())

    def __getattr__(self, item):
        if item in self._public_members:
            return super().__getattribute__(item)
        if item in self.default_config.keys():
            return self.config[item]
        return self.__getattribute__(item)

    def __setattr__(self, item, value):
        if item in self._public_members:
            super().__setattr__(item, value)
            return
        if item in self.default_config.keys():
            self.config[item] = value
        elif item not in dir(self):
            raise KeyError(item)
        else:
            super().__setattr__(item, value)


class OomoxSettings(CommonOomoxConfig):
    def __init__(self, config_name, default_config):
        super().__init__(
            config_dir=USER_CONFIG_DIR,
            config_name=config_name,
            default_config=default_config
        )


PRESET_LIST_MIN_SIZE = 150
UI_SETTINGS = OomoxSettings(
    config_name='ui_config', default_config=dict(
        window_width=600,
        window_height=400,
        preset_list_minimal_width=PRESET_LIST_MIN_SIZE,
        preset_list_width=PRESET_LIST_MIN_SIZE,
        preset_list_sections_expanded={},
    )
)

# SETTINGS = OomoxSettings(
#     config_name='app_config', default_config=dict(
#     )
# )
