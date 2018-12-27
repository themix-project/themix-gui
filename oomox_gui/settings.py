from .config import USER_CONFIG_DIR
from .export_config import OomoxConfig
from .presets_list import PRESET_LIST_MIN_SIZE


class SettingsKeys:
    preset_list_width = 'preset_list_width'


class OomoxSettings(OomoxConfig):

    def __init__(self, config_name):
        super().__init__(
            config_dir=USER_CONFIG_DIR,
            config_name=config_name,
            default_config={
                SettingsKeys.preset_list_width: PRESET_LIST_MIN_SIZE
            }
        )

    config_keys = vars(SettingsKeys)

    def __getattr__(self, item):
        if item in self.config_keys:
            return self.config[item]
        return self.__getattribute__(item)

    def __setattr__(self, item, value):
        if item in self.config_keys:
            self.config[item] = value
        else:
            super().__setattr__(item, value)


SETTINGS = OomoxSettings(config_name='app_config')
