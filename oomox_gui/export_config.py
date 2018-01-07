import os
import json

from .config import USER_EXPORT_CONFIG_DIR


class ExportConfig(object):

    name = None
    config_path = None
    config = None
    default_config = None

    def __init__(self, default_config=None):
        self.default_config = default_config
        self.config = self.default_config or {}
        self.config_path = os.path.join(
            USER_EXPORT_CONFIG_DIR,
            "{}.json".format(self.name)
        )
        self.load()

    def load(self):
        try:
            with open(self.config_path, 'r') as file_object:
                self.config = json.load(file_object)
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
