import os
import json

from ..config import user_export_config_dir


class ExportConfig(object):

    name = None
    config_path = None
    config = None
    default_config = None

    def __init__(self, default_config=None):
        self.default_config = default_config
        self.config = self.default_config or {}
        self.config_path = os.path.join(
            user_export_config_dir,
            "{}.json".format(self.name)
        )
        self.load()

    def load(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            pass
        return self.config

    def save(self):
        if not os.path.exists(user_export_config_dir):
            os.makedirs(user_export_config_dir)
        with open(self.config_path, 'w') as f:
            return json.dump(self.config, f)

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = value

    def __str__(self):
        return str(self.config)
