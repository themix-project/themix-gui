import json

from .config import USER_PALETTE_PATH


class PaletteCache():

    _palette_cache = None

    @staticmethod
    def load():
        try:
            with open(USER_PALETTE_PATH, 'r') as file_object:
                return json.load(file_object)
        except FileNotFoundError:
            return []

    @staticmethod
    def save(palette_cache_list):
        with open(USER_PALETTE_PATH, 'w') as file_object:
            return json.dump(palette_cache_list, file_object)

    @classmethod
    def set(cls, palette_cache_list):
        cls._palette_cache = palette_cache_list
        cls.save(palette_cache_list)

    @classmethod
    def get(cls):
        if not cls._palette_cache:
            cls._palette_cache = cls.load()
        return cls._palette_cache

    @classmethod
    def get_gtk(cls):
        return ':'.join(cls.get())

    @classmethod
    def add_color(cls, gtk_color):
        gtk_color_converted = gtk_color.to_color().to_string()
        palette_cache_list = [
            string for string in cls.get()  # pylint: disable=not-an-iterable
            if string != ''
        ]
        if gtk_color_converted not in palette_cache_list:
            cls.set(
                ([gtk_color_converted] + palette_cache_list)[:20]
            )
