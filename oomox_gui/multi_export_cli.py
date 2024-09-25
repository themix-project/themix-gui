import argparse
import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from gi.repository import Gdk, GLib

from oomox_gui.config import COLORS_DIR, DEFAULT_ENCODING, USER_COLORS_DIR, USER_EXPORT_CONFIG_DIR
from oomox_gui.i18n import translate
from oomox_gui.main import OomoxGtkApplication
from oomox_gui.multi_export import CONFIG_FILE_PREFIX, MultiExportDialog
from oomox_gui.terminal import generate_terminal_colors_for_oomox
from oomox_gui.theme_file_parser import read_colorscheme_from_path

if TYPE_CHECKING:
    from .theme_file import ThemeT


def strip_multi_export_json(input_path: str | Path) -> Any:
    home_str = Path.home().as_posix()
    with Path(input_path).open(encoding=DEFAULT_ENCODING) as fobj:
        data = json.load(fobj)
    if not isinstance(data, dict):
        return data
    result = {}
    for plugin_idx, plugin_config in data.items():
        result_config = {}
        if not isinstance(plugin_config, dict):
            result[plugin_idx] = plugin_config
            continue
        for key, value in plugin_config.items():
            if (key != "config") or (not isinstance(value, dict)):
                result_config[key] = value
            else:
                last_app = value.get("last_app")
                result_config[key] = {
                    config_key: (
                        config_value.replace(home_str, "~")
                        if isinstance(config_value, str) and config_value.startswith(home_str)
                        else config_value
                    )
                    for config_key, config_value in value.items()
                    if (
                        (not last_app)
                        or (not config_key.startswith("default_path_"))
                        or (config_key == f"default_path_{last_app}")
                    )
                }
        result[plugin_idx] = result_config
    return result


def do_multi_export(args: argparse.Namespace) -> None:
    export_layout_path = args.export_layout_path
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

    themix_theme_path = args.themix_theme_path
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

    app = OomoxGtkApplication(show_window=False)

    def callback1(theme: "ThemeT") -> None:
        generate_terminal_colors_for_oomox(
            colorscheme=theme,
            window=app.window,
            result_callback=callback2,
        )

    def callback2(theme: "ThemeT") -> None:
        multi_export = MultiExportDialog(
            transient_for=app.window,  # type: ignore[arg-type]
            colorscheme=theme,
            theme_name=themix_theme_name,
            export_layout=export_layout_name if not export_layout_path.startswith("/") else None,
            export_layout_path=export_layout_path if export_layout_path.startswith("/") else None,
            readonly=True,
            export_callback=callback3,
        )
        Gdk.threads_add_idle(GLib.PRIORITY_LOW, multi_export.export_all)
        app.run([])

    def callback3(_me: MultiExportDialog) -> None:
        app.quit()

    read_colorscheme_from_path(themix_theme_path, callback=callback1)
    print(":: DONE 👌😸")


def main() -> None:
    # print(sys.orig_argv)  # @TODO: it will be needed later
    my_name = Path(sys.argv[0]).name
    parser = argparse.ArgumentParser(
        description="Themix Multi-Export CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
------------------------

When using Multi-Export from GUI your multi-export layout would be automatically \
saved to `~/.config/oomox/export_config/multi_export_*.json` files.

------------------------

Examples:

Export `oodwaita` multi-export config using `Gigavolt` colortheme:

    $ {my_name} ./export_config_examples/multi_export_oodwaita.json ./colors/Featured/Gigavolt

Strip multi-export config from the extra metadata, to either share it \
or use in the scripts etc:

    $ {my_name} --strip ~/.config/oomox/export_config/multi_export_default.json

""",
    )
    parser.add_argument(
        "export_layout_path",
        help=(
            "path to export layout config file,"
            f" or a name with `{CONFIG_FILE_PREFIX}` prefix inside `{USER_EXPORT_CONFIG_DIR}`"
        ),
    )
    parser.add_argument(
        "themix_theme_path",
        nargs="?",
        help=(
            "path to theme file,"
            f" for example inside `{COLORS_DIR}` or `{USER_COLORS_DIR}`"
        ),
    )
    parser.add_argument(
        "-s", "--strip",
        action="store_true",
        help=(
            "instead of doing export"
            ", strip extra metadata from export layout config, for uploading it or using in manual scripts"
        ),
    )
    args = parser.parse_args()

    if args.strip:
        print(
            json.dumps(
                strip_multi_export_json(
                    input_path=args.export_layout_path,
                ), indent=2,
            ),
        )
        return

    if not args.themix_theme_path:
        print("".join((
            "\n",
            translate("Error:"),
            " ",
            translate("{arg} is required").format(arg="themix_theme_path"),
            "\n",
        )))
        parser.print_help()
        return

    do_multi_export(args)


if __name__ == "__main__":
    main()
