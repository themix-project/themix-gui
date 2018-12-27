import os
import json

from .config import USER_EXPORT_CONFIG_DIR


class OomoxConfig:

    name = None
    config_path = None
    config = None
    default_config = None

    def __init__(self, config_dir, config_name, default_config=None):
        self.name = config_name
        self.default_config = default_config
        self.config = self.default_config or {}
        self.config_path = os.path.join(
            config_dir,
            "{}.json".format(self.name)
        )
        self.load()

    def load(self):
        try:
            with open(self.config_path, 'r') as file_object:
                for key, value in json.load(file_object).items():
                    self.config[key] = value
        except FileNotFoundError:
            pass
        return self.config

    def save(self):
        if not os.path.exists(USER_EXPORT_CONFIG_DIR):
            os.makedirs(USER_EXPORT_CONFIG_DIR)
        with open(self.config_path, 'w') as file_object:
            return json.dump(self.config, file_object)

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = value

    def __str__(self):
        return str(self.config)

    def __repr__(self):
        return "Config<{}>".format(str(self))


class ExportConfig(OomoxConfig):

    def __init__(self, config_name, default_config=None):
        super().__init__(
            config_name=config_name,
            default_config=default_config,
            config_dir=USER_EXPORT_CONFIG_DIR,
        )
