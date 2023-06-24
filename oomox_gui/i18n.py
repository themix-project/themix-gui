import gettext
import os


class OomoxTranslation:

    translation: gettext.NullTranslations | None = None

    @classmethod
    def get(cls) -> gettext.NullTranslations:
        if not cls.translation:
            cls.translation = gettext.translation(
                "oomox",
                localedir=os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "..", "locale",
                ),
                fallback=True,
            )
        return cls.translation


def translate(msg: str) -> str:
    return OomoxTranslation.get().gettext(msg)


def translate_many(singular: str, plural: str, count: int) -> str:
    return OomoxTranslation.get().ngettext(singular, plural, count)
