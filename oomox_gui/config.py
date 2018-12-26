import os


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

OOMOX_ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))

COLORS_DIR = os.path.join(
    OOMOX_ROOT_DIR, "colors/"
)
PLUGINS_DIR = os.path.join(
    OOMOX_ROOT_DIR, "plugins/"
)
TERMINAL_TEMPLATE_DIR = os.path.join(
    OOMOX_ROOT_DIR, "terminal_templates/"
)


USER_CONFIG_DIR = os.path.abspath(os.path.join(
    os.environ.get(
        "XDG_CONFIG_HOME",
        os.path.join(
            os.environ.get("HOME", os.path.expanduser("~")),
            ".config/"
        )
    ),
    "oomox/"
))
USER_COLORS_DIR = os.path.join(
    USER_CONFIG_DIR, "colors/"
)
USER_PLUGINS_DIR = os.path.join(
    USER_CONFIG_DIR, "plugins/"
)
USER_PALETTE_PATH = os.path.join(
    USER_CONFIG_DIR, "recent_palette.json"
)
USER_EXPORT_CONFIG_DIR = os.path.join(
    USER_CONFIG_DIR, "export_config/"
)


FALLBACK_COLOR = "F33333"
