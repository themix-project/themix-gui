import os


script_dir = os.path.dirname(os.path.realpath(__file__))
oomox_root_dir = os.path.join(script_dir, "../")
gtk_preview_css_dir = os.path.join(script_dir, "gtk_preview_css/")
gtk_theme_dir = os.path.join(oomox_root_dir, "gtk-theme/")
materia_theme_dir = os.path.join(oomox_root_dir, "materia-theme/")
user_config_dir = os.path.join(
    os.environ.get(
        "XDG_CONFIG_HOME",
        os.path.join(os.environ.get("HOME"), ".config/")
    ),
    "oomox/"
)
user_theme_dir = os.path.join(user_config_dir, "colors/")
colors_dir = os.path.join(oomox_root_dir, "colors/")
user_palette_path = os.path.join(user_config_dir, "recent_palette.json")
terminal_template_dir = os.path.join(script_dir, "terminal_templates/")
FALLBACK_COLOR = "F33333"
