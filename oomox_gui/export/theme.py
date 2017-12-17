import os

from gi.repository import Gtk

from ..config import (
    gtk_theme_dir, materia_theme_dir,
)

from .common import ExportDialog


def export_theme(window, theme_path, colorscheme):
    if colorscheme["THEME_STYLE"] == "materia":
        export_materia_theme(
            window=window, theme_path=theme_path
        )
    else:
        export_oomox_theme(
            window=window, theme_path=theme_path
        )


def export_oomox_theme(window, theme_path):
    if Gtk.get_minor_version() >= 20:
        make_opts = "gtk320"
    else:
        make_opts = "gtk3"
    return ExportDialog(window).do_export([
        "bash",
        os.path.join(gtk_theme_dir, "change_color.sh"),
        theme_path,
        "--make-opts", make_opts
    ], timeout=100)


def export_materia_theme(window, theme_path):
    return ExportDialog(window).do_export([
        "bash",
        os.path.join(materia_theme_dir, "change_color.sh"),
        theme_path,
    ], timeout=1000)
