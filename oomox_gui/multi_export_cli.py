import os
import sys
from typing import TYPE_CHECKING, Final

from gi.repository import Gdk, GLib

from oomox_gui.config import COLORS_DIR, USER_COLORS_DIR, USER_EXPORT_CONFIG_DIR
from oomox_gui.main import OomoxGtkApplication
from oomox_gui.multi_export import CONFIG_FILE_PREFIX, MultiExportDialog
from oomox_gui.theme_file_parser import read_colorscheme_from_path

if TYPE_CHECKING:
    from .theme_file import ThemeT


NUM_ARGS: Final = 2


def print_help() -> None:
    print(f"Usage: {sys.argv[0]} EXPORT_LAYOUT_PATH THEMIX_THEME_PATH")
    print()
    print(
        f"\tEXPORT_LAYOUT_PATH:\tpath to export layout config file with,"
        f" or a name with `{CONFIG_FILE_PREFIX}` prefix inside `{USER_EXPORT_CONFIG_DIR}`",
    )
    print(
        f"\tTHEMIX_THEME_PATH:\tpath to theme file,"
        f" for example inside `{COLORS_DIR}` or `{USER_COLORS_DIR}`",
    )


def main() -> None:
    if (
        ((len(sys.argv) >= (1 + 1)) and sys.argv[1] in {"-h", "--help"})
        or (len(sys.argv) < (NUM_ARGS + 1))
    ):
        print_help()
        sys.exit(1)

    export_layout_path = sys.argv[1]
    export_layout_path = os.path.expanduser(export_layout_path)
    if os.path.exists(
            os.path.join(
                USER_EXPORT_CONFIG_DIR, export_layout_path,
            ),
    ):
        export_layout_path = os.path.join(
            USER_EXPORT_CONFIG_DIR, export_layout_path,
        )
    else:
        export_layout_path = os.path.realpath(export_layout_path)
    if not os.path.exists(export_layout_path):
        print(f"{export_layout_path} not exists")
        sys.exit(1)
    export_layout_name = os.path.basename(export_layout_path).rsplit(
        ".json", maxsplit=1,
    )[0].split(
        CONFIG_FILE_PREFIX, maxsplit=1,
    )[1]
    print(f":: Found export layout '{export_layout_name}' at {export_layout_path}")

    themix_theme_path = sys.argv[2]
    themix_theme_name = os.path.basename(themix_theme_path).rsplit(
        ".themix", maxsplit=1,
    )[0]
    themix_theme_path = os.path.realpath(
        os.path.expanduser(
            themix_theme_path,
        ),
    )
    if not os.path.exists(themix_theme_path):
        print(f"{themix_theme_path} not exists")
        sys.exit(1)
    print(f":: Found Themix theme '{themix_theme_name}' at {themix_theme_path}")

    def callback(theme: "ThemeT") -> None:
        app = OomoxGtkApplication(show_window=False)

        def export_callback(_me: MultiExportDialog) -> None:
            app.quit()

        multi_export = MultiExportDialog(
            transient_for=app.window,  # type: ignore[arg-type]
            colorscheme=theme,
            theme_name=themix_theme_name,
            export_layout=export_layout_name if not export_layout_path.startswith("/") else None,
            export_layout_path=export_layout_path if export_layout_path.startswith("/") else None,
            readonly=True,
            export_callback=export_callback,
        )
        Gdk.threads_add_idle(GLib.PRIORITY_LOW, multi_export.export_all)
        app.run([])

    read_colorscheme_from_path(themix_theme_path, callback=callback)
    print(":: DONE 👌😸")


if __name__ == "__main__":
    main()
