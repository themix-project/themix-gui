import json

from gi.repository import Gdk

from .config import USER_PALETTE_PATH, DEFAULT_ENCODING


PaletteCacheT = list[str]


class PaletteCache():

    _palette_cache: PaletteCacheT | None = None

    @staticmethod
    def load() -> PaletteCacheT:
        try:
            with open(USER_PALETTE_PATH, 'r', encoding=DEFAULT_ENCODING) as file_object:
                result = json.load(file_object)
            if not isinstance(result, list):
                raise RuntimeError("Error loading palette cache")
            for item in result:
                if not isinstance(item, str):
                    raise RuntimeError("Error loading palette cache")
            return result
        except (FileNotFoundError, RuntimeError):
            return []

    @staticmethod
    def save(palette_cache_list: PaletteCacheT) -> None:
        with open(USER_PALETTE_PATH, 'w', encoding=DEFAULT_ENCODING) as file_object:
            return json.dump(palette_cache_list, file_object)

    @classmethod
    def set(cls, palette_cache_list: PaletteCacheT) -> None:
        cls._palette_cache = palette_cache_list
        cls.save(palette_cache_list)

    @classmethod
    def get(cls) -> PaletteCacheT:
        if not cls._palette_cache:
            cls._palette_cache = cls.load()
        return cls._palette_cache

    @classmethod
    def get_gtk(cls) -> str:
        return ':'.join(cls.get())

    @classmethod
    def add_color(cls, gtk_color: Gdk.RGBA) -> None:
        gtk_color_converted = gtk_color.to_color().to_string()  # type: ignore[func-returns-value]
        palette_cache_list = [
            string for string in cls.get()  # pylint: disable=not-an-iterable
            if string != ''
        ]
        if gtk_color_converted not in palette_cache_list:
            cls.set(
                ([gtk_color_converted] + palette_cache_list)[:20]
            )
