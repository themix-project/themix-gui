import sys
import os
import json

from .i18n import _
from .config import USER_CONFIG_DIR


if sys.version_info.minor >= 5:
    from typing import TYPE_CHECKING  # pylint: disable=wrong-import-order
    if TYPE_CHECKING:
        # pylint: disable=ungrouped-imports
        from typing import Dict  # noqa


class CommonOomoxConfig:

    name = None
    config_dir = None
    config_path = None
    default_config = {}  # type: Dict[str,str]
    config = None

    def __init__(self, config_dir, config_name, default_config=None):
        self.name = config_name
        self.config_dir = config_dir
        self.config_path = os.path.join(
            self.config_dir,
            "{}.json".format(self.name)
        )
        self.default_config = default_config or {}
        self.config = self.default_config or {}
        self.load()

    def __str__(self):
        return str(self.config)

    def __repr__(self):
        return "Config<{}>".format(str(self))

    def load(self):
        try:
            with open(self.config_path, 'r') as file_object:
                for key, value in json.load(file_object).items():
                    self.config[key] = value
        except Exception as exc:
            print(_("Can't read config file"))
            print(exc)
        return self.config

    def save(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        with open(self.config_path, 'w') as file_object:
            return json.dump(self.config, file_object)

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = value

    def __getattr__(self, item):
        if item in self.default_config.keys():
            return self.config[item]
        return self.__getattribute__(item)

    def __setattr__(self, item, value):
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
