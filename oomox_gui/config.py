import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


FALLBACK_COLOR: "Final" = "F33333"
DEFAULT_ENCODING: "Final" = "utf-8"


SCRIPT_DIR: "Final" = os.path.dirname(os.path.realpath(__file__))
OOMOX_ROOT_DIR: "Final" = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))


COLORS_DIR: "Final" = os.path.join(
    OOMOX_ROOT_DIR, "colors/",
)
PLUGINS_DIR: "Final" = os.path.join(
    OOMOX_ROOT_DIR, "plugins/",
)
TERMINAL_TEMPLATE_DIR: "Final" = os.path.join(
    OOMOX_ROOT_DIR, "terminal_templates/",
)


USER_CONFIG_DIR: "Final" = os.path.abspath(os.path.join(
    os.environ.get(
        "XDG_CONFIG_HOME",
        os.path.join(
            os.environ.get("HOME", os.path.expanduser("~")),
            ".config/",
        ),
    ),
    "oomox/",
))
USER_COLORS_DIR: "Final" = os.path.join(
    USER_CONFIG_DIR, "colors/",
)
USER_PLUGINS_DIR: "Final" = os.path.join(
    USER_CONFIG_DIR, "plugins/",
)
USER_PALETTE_PATH: "Final" = os.path.join(
    USER_CONFIG_DIR, "recent_palette.json",
)
USER_EXPORT_CONFIG_DIR: "Final" = os.path.join(
    USER_CONFIG_DIR, "export_config/",
)
