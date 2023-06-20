import json
import os
from typing import TYPE_CHECKING

from .config import DEFAULT_ENCODING, USER_CONFIG_DIR
from .i18n import translate

if TYPE_CHECKING:
    from typing import Any, Final


PRESET_LIST_MIN_SIZE: "Final" = 150


class CommonOomoxConfig:

    name: str
    config_dir: str
    config_path: str
    default_config: dict[str, str]
    config: dict[str, "Any"]

    def __init__(
            self,
            config_dir: str,
            config_name: str,
            default_config: dict[str, "Any"] | None = None,
            force_reload: bool = False,
    ) -> None:
        self.name = config_name
        self.config_dir = config_dir
        self.config_path = os.path.join(
            self.config_dir,
            f"{self.name}.json",
        )
        self.default_config = default_config or {}
        self.config = self.load(
            default_config=self.default_config,
            config_path=self.config_path,
            force_reload=force_reload,
        )

    def __str__(self) -> str:
        return str(self.config)

    def __repr__(self) -> str:
        return f"Config<{self!s}>"

    @classmethod
    def load(
            cls,
            config_path: str,
            default_config: dict[str, "Any"],
            force_reload: bool,
    ) -> dict[str, "Any"]:
        if force_reload or not getattr(cls, "config", None):
            cls.config = default_config or {}
            try:
                with open(config_path, encoding=DEFAULT_ENCODING) as file_object:
                    for key, value in json.load(file_object).items():
                        cls.config[key] = value
            except Exception as exc:
                print(translate("Can't read config file"))
                print(exc)
        return cls.config

    def save(self) -> None:
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        with open(self.config_path, "w", encoding=DEFAULT_ENCODING) as file_object:
            return json.dump(self.config, file_object)

    def get(self, item: str, fallback: "Any" = None) -> "Any":
        return self.config.get(item, fallback)

    def __getitem__(self, item: str) -> "Any":
        return self.config[item]

    def __setitem__(self, item: str, value: "Any") -> None:
        self.config[item] = value

    @property
    def _public_members(self) -> list[str]:
        return dir(self) + list(self.__annotations__.keys())

    def __getattr__(self, item: str) -> "Any":
        if item in self._public_members:
            return super().__getattribute__(item)
        if item in self.default_config:
            return self.config[item]
        return self.__getattribute__(item)

    def __setattr__(self, item: str, value: "Any") -> None:
        if item in self._public_members:
            super().__setattr__(item, value)
            return
        if item in self.default_config:
            self.config[item] = value
        elif item not in dir(self):
            raise KeyError(item)
        else:
            super().__setattr__(item, value)


class OomoxSettings(CommonOomoxConfig):
    def __init__(self, config_name: str, default_config: dict[str, "Any"]) -> None:
        super().__init__(
            config_dir=USER_CONFIG_DIR,
            config_name=config_name,
            default_config=default_config,
        )


class UISettings(OomoxSettings):

    def __init__(self) -> None:
        super().__init__(
            config_name="ui_config",
            default_config={
                "window_width": 600,
                "window_height": 400,
                "preset_list_minimal_width": PRESET_LIST_MIN_SIZE,
                "preset_list_width": PRESET_LIST_MIN_SIZE,
                "preset_list_sections_expanded": {},
            },
        )

# SETTINGS = OomoxSettings(
#     config_name='app_config', default_config=dict(
#     )
# )
