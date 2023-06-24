import json
from typing import TYPE_CHECKING

from .config import DEFAULT_ENCODING, USER_PALETTE_PATH
from .helpers import log_error

if TYPE_CHECKING:
    from gi.repository import Gdk


PaletteCacheT = list[str]


class PaletteCache:

    _palette_cache: PaletteCacheT | None = None

    @staticmethod
    def load() -> PaletteCacheT:
        try:
            with open(USER_PALETTE_PATH, encoding=DEFAULT_ENCODING) as file_object:
                result = json.load(file_object)
        except FileNotFoundError:
            return []
        if not isinstance(result, list):
            log_error("Error loading palette cache")
            return []
        for item in result:
            if not isinstance(item, str):
                log_error("Error loading palette cache")
                return []
        return result

    @staticmethod
    def save(palette_cache_list: PaletteCacheT) -> None:
        with open(USER_PALETTE_PATH, "w", encoding=DEFAULT_ENCODING) as file_object:
            return json.dump(palette_cache_list, file_object)

    @classmethod
    def put(cls, palette_cache_list: PaletteCacheT) -> None:
        cls._palette_cache = palette_cache_list
        cls.save(palette_cache_list)

    @classmethod
    def get(cls) -> PaletteCacheT:
        if not cls._palette_cache:
            cls._palette_cache = cls.load()
        return cls._palette_cache

    @classmethod
    def get_gtk(cls) -> str:
        return ":".join(cls.get())

    @classmethod
    def add_color(cls, gtk_color: "Gdk.RGBA") -> None:
        gtk_color_converted = gtk_color.to_color().to_string()  # type: ignore[func-returns-value]
        palette_cache_list = [
            string for string in cls.get()  # pylint: disable=not-an-iterable
            if string
        ]
        if gtk_color_converted not in palette_cache_list:
            cls.put([gtk_color_converted, *palette_cache_list][:20])
