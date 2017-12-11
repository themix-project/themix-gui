import os


script_dir = os.path.dirname(os.path.realpath(__file__))
gtk_preview_css_dir = os.path.join(script_dir, "gtk_preview_css/")
terminal_template_dir = os.path.join(script_dir, "terminal_templates/")

oomox_root_dir = os.path.join(script_dir, "../")
colors_dir = os.path.join(oomox_root_dir, "colors/")
gtk_theme_dir = os.path.join(oomox_root_dir, "gtk-theme/")
materia_theme_dir = os.path.join(oomox_root_dir, "materia-theme/")
archdroid_theme_dir = os.path.join(oomox_root_dir, "archdroid-icon-theme/")

user_config_dir = os.path.join(
    os.environ.get(
        "XDG_CONFIG_HOME",
        os.path.join(os.environ.get("HOME"), ".config/")
    ),
    "oomox/"
)
user_theme_dir = os.path.join(user_config_dir, "colors/")
user_palette_path = os.path.join(user_config_dir, "recent_palette.json")

FALLBACK_COLOR = "F33333"
