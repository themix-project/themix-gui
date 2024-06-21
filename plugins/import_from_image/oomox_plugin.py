# pylint:disable=import-outside-toplevel
import gc
import os
from multiprocessing.pool import Pool
from time import time
from typing import TYPE_CHECKING

from oomox_gui.color import (
    RGB,
    color_hex_from_list,
    color_list_from_hex,
    find_closest_color,
    hex_darker,
    hex_to_int,
    int_list_from_hex,
    is_dark,
)
from oomox_gui.config import TERMINAL_TEMPLATE_DIR
from oomox_gui.helpers import (
    apply_chain,
    call_method_from_class,
    delayed_partial,
    get_plugin_module,
)
from oomox_gui.i18n import translate
from oomox_gui.main import NoWindowError, OomoxApplicationWindow
from oomox_gui.migrations import PluginMigrationConfig
from oomox_gui.plugin_api import OomoxImportPluginAsync
from oomox_gui.terminal import import_xcolors
from oomox_gui.theme_model import get_first_theme_option

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from types import ModuleType
    from typing import Annotated, Any, Final

    from oomox_gui.color import HexColor, IntColor
    from oomox_gui.theme_file import ThemeT


PLUGIN_DIR: "Final" = os.path.dirname(os.path.realpath(__file__))


LOW_QUALITY: "Final" = 100
MEDIUM_QUALITY: "Final" = 200
HIGH_QUALITY: "Final" = 400
# ULTRA_QUALITY: "Final" = 1000

ACCURACY: "Final" = 40

image_analyzer: "ModuleType" = get_plugin_module("ima", os.path.join(PLUGIN_DIR, "ima.py"))


def sort_by_saturation(c: "IntColor") -> int:  # pylint: disable=invalid-name
    if len(c) != RGB.length:
        raise TypeError(c)
    return (
        abs(c[RGB.RED] - c[RGB.GREEN]) + abs(c[RGB.RED] - c[RGB.BLUE])
        + abs(c[RGB.GREEN] - c[RGB.RED]) + abs(c[RGB.GREEN] - c[RGB.BLUE])
        + abs(c[RGB.BLUE] - c[RGB.GREEN]) + abs(c[RGB.BLUE] - c[RGB.RED])
    )


def get_gray_colors(palette: "list[HexColor]") -> "list[HexColor]":
    list_of_colors = [[hex_to_int(s) for s in color_list_from_hex(c)] for c in palette]
    saturation_list = sorted(
        list_of_colors,
        key=sort_by_saturation,
    )
    gray_colors = saturation_list[:(len(saturation_list) // 3)]
    gray_colors.sort(key=sum)
    return [color_hex_from_list(c) for c in gray_colors]


class Plugin(OomoxImportPluginAsync):

    name = "import_from_image"
    display_name = translate("Image colors")
    import_text = translate("Colors from Image")
    about_text = translate(
        "Generate a theme based on any image "
        "using different algorithms for determining the main colors.",
    )
    about_links = [
        {
            "name": translate("Homepage"),
            "url": "https://github.com/themix-project/oomox/",
        },
    ]

    file_extensions = (
        ".jpg",
        ".png",
        ".gif",
    )

    def __init__(self) -> None:
        super().__init__()
        self.migrate()

    config_version = 1

    def migrate(self) -> None:
        config = PluginMigrationConfig(plugin=self)
        if config.version < 1:
            parent_dir = os.path.dirname(self.user_theme_dir)
            old_plugin_dir_name = "__plugin__import_pil"
            old_user_theme_dir = os.path.join(parent_dir, old_plugin_dir_name)
            if os.path.exists(old_user_theme_dir):
                os.rename(old_user_theme_dir, self.user_theme_dir)
        config.update(version=self.config_version)

    default_theme = {
        "TERMINAL_THEME_MODE": "manual",
        "TERMINAL_THEME_AUTO_BGFG": False,
    }
    default_themes = {
        "lcars": {
            "TERMINAL_THEME_MODE": "manual",
            "ROUNDNESS": 20,
            "ICONS_STYLE": "archdroid",
        },
    }
    translation_common = {
        "NAME": "scheme",

        "TERMINAL_COLOR0": "color0",
        "TERMINAL_COLOR1": "color1",
        "TERMINAL_COLOR2": "color2",
        "TERMINAL_COLOR3": "color3",
        "TERMINAL_COLOR4": "color4",
        "TERMINAL_COLOR5": "color5",
        "TERMINAL_COLOR6": "color6",
        "TERMINAL_COLOR7": "color7",
        "TERMINAL_COLOR8": "color8",
        "TERMINAL_COLOR9": "color9",
        "TERMINAL_COLOR10": "color10",
        "TERMINAL_COLOR11": "color11",
        "TERMINAL_COLOR12": "color12",
        "TERMINAL_COLOR13": "color13",
        "TERMINAL_COLOR14": "color14",
        "TERMINAL_COLOR15": "color15",

        "TERMINAL_BACKGROUND": "background",
        "TERMINAL_FOREGROUND": "foreground",
        "TERMINAL_ACCENT_COLOR": "color3",
    }
    theme_translations: dict[str, dict[str, str]] = {
        "1": {
            "BG": "color7",
            "FG": "color0",
            # "TXT_BG": "foreground",
            # "TXT_FG": "background",
            "TXT_BG": "color15",
            "TXT_FG": "color0",
            "SEL_BG": "color4",
            "SEL_FG": "color15",
            "HDR_BG": "color0",
            "HDR_FG": "color7",
            "BTN_BG": "color8",
            "BTN_FG": "foreground",
            "HDR_BTN_BG": "background",
            "HDR_BTN_FG": "foreground",

            "ICONS_LIGHT_FOLDER": "color12",
            "ICONS_LIGHT": "color14",
            "ICONS_MEDIUM": "color6",
            "ICONS_DARK": "color4",
        },
        "2": {
            "BG": "color7",
            "FG": "color0",
            "TXT_BG": "color15",
            "TXT_FG": "color0",
            "SEL_BG": "color1",
            "SEL_FG": "foreground",
            "HDR_BG": "color0",
            "HDR_FG": "color7",
            "BTN_BG": "color12",
            "BTN_FG": "color0",
            "WM_BORDER_FOCUS": "color10",
            "ICONS_LIGHT_FOLDER": "color13",
            "ICONS_LIGHT": "color9",
            "ICONS_MEDIUM": "color1",
            "ICONS_DARK": "color5",
        },
        "3": {
            "BG": "color7",
            "FG": "color0",
            "TXT_BG": "color15",
            "TXT_FG": "color0",
            "SEL_BG": "color3",
            "SEL_FG": "color0",
            "HDR_BG": "color0",
            "HDR_FG": "color7",
            "BTN_BG": "color12",
            "BTN_FG": "color0",
            "WM_BORDER_FOCUS": "color3",
            "ICONS_LIGHT_FOLDER": "color13",
            "ICONS_LIGHT": "color9",
            "ICONS_MEDIUM": "color1",
            "ICONS_DARK": "color5",
        },
        "4": {
            "BG": "color5",
            "FG": "color0",
            "HDR_BG": "color1",
            "HDR_FG": "foreground",
            "SEL_BG": "color4",
            "SEL_FG": "foreground",
            "TXT_BG": "color6",
            "TXT_FG": "color1",
            "BTN_BG": "color3",
            "BTN_FG": "color0",
            "HDR_BTN_BG": "color5",
            "HDR_BTN_FG": "background",
        },
        "lcars": {
            "BG": "background",
            "FG": "foreground",
            "TXT_BG": "background",
            "TXT_FG": "color11",
            "SEL_BG": "color1",
            "SEL_FG": "background",
            "HDR_BG": "background",
            "HDR_FG": "color7",
            "BTN_BG": "color10",
            "BTN_FG": "color0",
            "HDR_BTN_BG": "color12",
            "HDR_BTN_FG": "background",
            "WM_BORDER_FOCUS": "color10",
            "ICONS_ARCHDROID": "color12",
        },
    }

    theme_model_import = [
        {
            "display_name": translate("Import Colors from Image"),
            "type": "separator",
            "value_filter": {
                "FROM_PLUGIN": ["import_pil", "import_from_image"],
            },
        },
        {
            "key": "_PIL_PALETTE_QUALITY",
            "type": "options",
            "options": [{
                "value": LOW_QUALITY,
                "display_name": translate("oomox: low quality"),
            }, {
                "value": MEDIUM_QUALITY,
                "display_name": translate("oomox: medium quality"),
            }, {
                "value": HIGH_QUALITY,
                "display_name": translate("oomox: high quality"),
            }],
            # }, {
            #     'value': ULTRA_QUALITY,
            #     'display_name': 'ultra',
            "fallback_value": LOW_QUALITY,
            "display_name": translate("Image Analysis"),
            "reload_theme": True,
        },
        {
            "key": "_PIL_PALETTE_STYLE",
            "type": "options",
            "options": [
                {"value": template_name}
                for template_name in sorted(os.listdir(TERMINAL_TEMPLATE_DIR))
            ],
            # 'fallback_value': 'monovedek_pale_gray',
            "fallback_value": "basic",
            "display_name": translate("Palette Style"),
            "reload_theme": True,
        },
        {
            "key": "_PIL_PALETTE_STRICT",
            "type": "bool",
            "fallback_value": False,
            "display_name": translate("Stronger Follow Palette Template"),
            "reload_theme": True,
            "value_filter": {
                "_PIL_PALETTE_QUALITY": [LOW_QUALITY, MEDIUM_QUALITY, HIGH_QUALITY],
            },
        },
        {
            "key": "_PIL_PALETTE_INVERSE",
            "type": "bool",
            "fallback_value": False,
            "display_name": translate("Dark/Light Colors"),
            "reload_theme": True,
        },
        {
            "key": "_PIL_THEME_TEMPLATE",
            "type": "options",
            "options": [
                {"value": template_name}
                for template_name in sorted(theme_translations.keys())
            ],
            "fallback_value": "1",
            "display_name": translate("GUI Theme Template"),
            "reload_theme": True,
        },
        {
            "key": "_PIL_IMAGE_PREVIEW",
            "type": "image_path",
            "fallback_value": None,
            "display_name": translate("Image Thumbnail"),
        },
    ]
    theme_model_gtk = [
        {
            "display_name": translate("Edit Generated Theme"),
            "type": "separator",
        },
    ]

    try:
        import colorz  # pylint: disable=import-error,useless-suppression
        theme_model_import[1]["options"] += [{
            "value": "colorz16",
            "display_name": translate("colorz lib: low quality"),
        }, {
            "value": "colorz32",
            "display_name": translate("colorz lib: medium quality"),
        }, {
            "value": "colorz64",
            "display_name": translate("colorz lib: high quality"),
        }]
    except:  # noqa: E722 pylint: disable=bare-except
        print(
            translate(
                "Import Colors From Image plugin:"
                " `{}` library is not installed - less color-import options are available.",
            ).format("colorz"),
        )

    try:
        import colorthief  # pylint: disable=import-error,useless-suppression
        theme_model_import[1]["options"] += [{
            "value": "colorthief16",
            "display_name": translate("colorthief lib"),
        }, {
            "value": "colorthief32",
            "display_name": translate("colorthief lib: doublepass"),
        }]
    except:  # noqa: E722  pylint: disable=bare-except
        print(
            translate(
                "Import Colors From Image plugin:"
                " `{}` library is not installed - less color-import options are available.",
            ).format("colorthief"),
        )

    try:
        import haishoku  # pylint: disable=import-error,useless-suppression
        # theme_model_import['_PIL_PALETTE_QUALITY']['options'].append({
        theme_model_import[1]["options"].append({
            "value": "haishoku",
            "display_name": translate("haishoku lib"),
        })
    except:  # noqa: E722  pylint: disable=bare-except
        print(
            translate(
                "Import Colors From Image plugin:"
                " `{}` library is not installed - less color-import options are available.",
            ).format("haishoku"),
        )

    try:
        import colorthief  # pylint: disable=import-error,useless-suppression
        import colorz  # pylint: disable=import-error,useless-suppression
        import haishoku  # pylint: disable=import-error,useless-suppression
        # theme_model_import['_PIL_PALETTE_QUALITY']['options'].append({
        theme_model_import[1]["options"] += [{
            "value": "all_low",
            "display_name": translate("all available: low quality"),
        }, {
            "value": "all_medium",
            "display_name": translate("all available: medium quality"),
        }]
    except:  # noqa: E722  pylint: disable=bare-except
        print(
            translate(
                "Import Colors From Image plugin:"
                " not all optional libraries are installed (see above).",
            ),
        )

    _terminal_palette_cache: dict[str, dict[str, str]] = {}
    _palette_cache: dict[str, list[str]] = {}

    @classmethod
    def _get_haishoku_palette(cls, image_path: str) -> "list[HexColor]":
        from haishoku.haishoku import Haishoku  # pylint: disable=import-error,useless-suppression
        palette = Haishoku.getPalette(image_path)
        return [color_hex_from_list(color) for _percentage, color in palette]

    @classmethod
    def _get_colorthief_palette(cls, image_path: str, color_count: int) -> "list[HexColor]":
        from colorthief import ColorThief  # pylint: disable=import-error,useless-suppression
        color_thief = ColorThief(image_path)
        palette = color_thief.get_palette(color_count=color_count)
        return [color_hex_from_list(color) for color in palette]

    @classmethod
    def _get_colorz_lib_palette(cls, image_path: str, color_count: int) -> "list[HexColor]":
        from colorz import colorz  # pylint: disable=import-error,useless-suppression
        with open(image_path, "rb") as fobj:
            palette = colorz(fobj, color_count, 50, 200)
        return [color_hex_from_list(color) for pair in palette for color in pair]

    @classmethod
    def _get_all_available_palettes(  # pylint: disable=too-many-locals
            cls,
            image_path: str,
            *,
            use_whole_palette: bool,
            quality_per_plugin: "Annotated[Sequence[int], 3]",
    ) -> "list[HexColor]":
        hex_palette = []
        from colorthief import ColorThief  # pylint: disable=import-error,useless-suppression
        from colorz import colorz  # pylint: disable=import-error,useless-suppression
        from haishoku.haishoku import Haishoku  # pylint: disable=import-error,useless-suppression
        with Pool() as pool:
            oomox_future = pool.apply_async(apply_chain, (
                get_plugin_module,
                ("ima", os.path.join(PLUGIN_DIR, "ima.py"), "get_hex_palette"),
                (image_path, use_whole_palette, 48, quality_per_plugin[0]),
            ))
            from functools import partial
            _opener = partial(open, image_path, "rb")
            colorz_future = pool.apply_async(delayed_partial, (
                colorz,
                (
                    (_opener, ()),
                ),
                (quality_per_plugin[1], 50, 200),
            ))
            colorthief_future = pool.apply_async(call_method_from_class, (
                ColorThief,
                (image_path, ),
                "get_palette",
                (quality_per_plugin[2], ),
            ))
            haishoku_future = pool.apply_async(
                Haishoku.getPalette, (image_path, ),
            )
            pool.close()
            hex_palette += oomox_future.get()
            try:
                colorz_result: list[
                    tuple[tuple[int, int, int], tuple[int, int, int]]
                ] = colorz_future.get()  # type: ignore[assignment]
                hex_palette += [
                    color_hex_from_list(color) for pair in colorz_result for color in pair
                ]
            except Exception as exc:
                print(exc)
            try:
                colorthief_result: list[tuple[int, int, int]] = (
                    colorthief_future.get(),  # type: ignore[assignment]
                )
                hex_palette += [
                    color_hex_from_list(color) for color in colorthief_result
                ]
            except Exception as exc:
                print(exc)
            try:
                hex_palette += [
                    color_hex_from_list(color) for _percentage, color in haishoku_future.get()
                ]
            except Exception as exc:
                print(exc)
            pool.join()
        return hex_palette

    def read_colorscheme_from_path(  # type: ignore[override]
            self,
            preset_path: str,
            callback: "Callable[[ThemeT], None]",
    ) -> None:

        get_first_theme_option("_PIL_IMAGE_PREVIEW")["fallback_value"] = preset_path

        def _callback(image_palette: "ThemeT") -> None:
            self.read_colorscheme_from_path_callback(image_palette, callback)

        palette_style: str = get_first_theme_option(  # type: ignore[assignment]
            "_PIL_PALETTE_STYLE",
        ).get("fallback_value")
        self.generate_terminal_palette(
            palette_style,
            preset_path,
            result_callback=_callback,
        )

    def read_colorscheme_from_path_callback(
            self,
            image_palette: "ThemeT",
            callback: "Callable[[ThemeT], None]",
    ) -> None:
        theme_template: str = get_first_theme_option(  # type: ignore[assignment]
            "_PIL_THEME_TEMPLATE", {},
        ).get("fallback_value")
        oomox_theme: dict[str, Any] = {}
        oomox_theme.update(self.default_theme)
        if theme_template in self.default_themes:
            oomox_theme.update(self.default_themes[theme_template])
        translation: dict[str, str] = {}
        translation.update(self.translation_common)
        translation.update(
            self.theme_translations[theme_template],
        )
        for oomox_key, image_palette_key in translation.items():
            if image_palette_key in image_palette:
                oomox_theme[oomox_key] = image_palette[image_palette_key]
        callback(oomox_theme)

    @staticmethod
    def _generate_palette_id(image_path: str, quality: str, *, use_whole_palette: bool) -> str:
        return image_path + quality + str(use_whole_palette)

    @classmethod
    def _generate_terminal_palette(
            cls, template_path: str, image_path: str, quality: str,
            *,
            use_whole_palette: bool, inverse_palette: bool,
            result_callback: "Callable[[dict[str, str]], None]",
    ) -> None:
        start_time = time()
        _id = cls._generate_palette_id(image_path, quality, use_whole_palette=use_whole_palette)
        hex_palette = cls._palette_cache.get(_id)
        if hex_palette:
            cls._generate_terminal_palette_callback(
                hex_palette, template_path,
                inverse_palette=inverse_palette,
                result_callback=result_callback,
            )
        else:
            def generate_terminal_palette_task() -> None:
                cls._generate_terminal_palette_task(
                    template_path, image_path, quality,
                    use_whole_palette=use_whole_palette,
                    inverse_palette=inverse_palette,
                    start_time=start_time,
                    result_callback=result_callback,
                )
            try:
                _app = OomoxApplicationWindow.get_instance()
                _app.disable(translate("Extracting palette from image…"))
                _app.schedule_task(generate_terminal_palette_task)
                _app.enable()
            except NoWindowError:
                generate_terminal_palette_task()

    @classmethod
    def _generate_terminal_palette_task(
            cls, template_path: str, image_path: str, quality: str,
            *,
            use_whole_palette: bool, inverse_palette: bool,
            start_time: float,
            result_callback: "Callable[[dict[str, str]], None]",
    ) -> None:
        if quality.startswith("colorz"):
            hex_palette = cls._get_colorz_lib_palette(
                image_path, color_count=int(quality.split("colorz")[1]),
            )
        elif quality.startswith("colorthief"):
            hex_palette = cls._get_colorthief_palette(
                image_path, color_count=int(quality.split("colorthief")[1]) + 1,
            )
        elif quality == "haishoku":
            hex_palette = cls._get_haishoku_palette(image_path)
        elif quality.startswith("all_"):
            _quality = quality.split("_")[1]
            if _quality == "low":
                quality_per_plugin = [100, 16, 16]
            elif _quality == "medium":
                quality_per_plugin = [200, 32, 32]
            else:
                raise NotImplementedError
            hex_palette = cls._get_all_available_palettes(
                image_path=image_path, use_whole_palette=use_whole_palette,
                quality_per_plugin=quality_per_plugin,
            )
        else:
            hex_palette = image_analyzer.get_hex_palette(
                image_path, quality=int(quality), use_whole_palette=use_whole_palette,
            )[:]
        print(
            f"{quality} quality, {len(hex_palette)} colors found, took {time() - start_time:.8f}s",
        )
        _id = cls._generate_palette_id(image_path, quality, use_whole_palette=use_whole_palette)
        cls._palette_cache[_id] = hex_palette
        cls._generate_terminal_palette_callback(
            hex_palette, template_path,
            inverse_palette=inverse_palette,
            result_callback=result_callback,
        )

    @classmethod
    def _generate_terminal_palette_callback(  # pylint: disable=too-many-locals
            cls,
            hex_palette: list[str],
            template_path: str,
            *,
            inverse_palette: bool,
            result_callback: "Callable[[dict[str, str]], None]",
    ) -> None:
        gray_colors = get_gray_colors(hex_palette)
        bright_colors = set(hex_palette)
        bright_colors.difference_update(gray_colors)
        bright_colors_list = list(bright_colors)
        hex_palette += [hex_darker(c, ACCURACY) for c in gray_colors]
        hex_palette += [hex_darker(c, -ACCURACY) for c in gray_colors]
        reference_palette = import_xcolors(os.path.join(TERMINAL_TEMPLATE_DIR, template_path))
        result_palette = {}
        if inverse_palette:
            reference_palette["foreground"], reference_palette["background"] = \
                reference_palette["background"], reference_palette["foreground"]
        is_dark_bg = is_dark(reference_palette["background"])

        max_possible_lightness = 255 * 3
        new_bg_color, _diff = find_closest_color(reference_palette["background"], hex_palette)
        if not new_bg_color:
            cant_find_color = "No color detected"
            raise RuntimeError(cant_find_color)
        # @TODO: use real lightness from HSV or Lab color model
        lightness_delta = sum(int_list_from_hex(new_bg_color)) * (1 if is_dark_bg else -1) + \
            max_possible_lightness // 4
        # max_possible_lightness // 6
        min_lightness = max_possible_lightness // 38
        max_lightness = max_possible_lightness - min_lightness
        if is_dark_bg:
            min_lightness = lightness_delta
        else:
            max_lightness = max_possible_lightness - lightness_delta

        for key, value in reference_palette.items():
            if key not in {"color0", "color7", "color8", "color15", "foreground", "background"}:
                closest_color, _diff = find_closest_color(
                    value, bright_colors_list,
                    min_lightness=min_lightness, max_lightness=max_lightness,
                )
            else:
                closest_color, _diff = find_closest_color(value, hex_palette)
            if not closest_color:
                no_similar_color = f"No similar color found for {key} {value}."
                raise RuntimeError(no_similar_color)
            result_palette[key] = closest_color

        gc.collect()
        result_callback(result_palette)

    @classmethod
    def generate_terminal_palette(
            cls, template_path: str, image_path: str,
            result_callback: "Callable[[ThemeT], None]",
    ) -> None:
        quality: int = get_first_theme_option(
            "_PIL_PALETTE_QUALITY", {},
        ).get("fallback_value")  # type: ignore[assignment]
        use_whole_palette = bool(
            get_first_theme_option("_PIL_PALETTE_STRICT", {}).get("fallback_value"),
        )
        inverse_palette = bool(
            get_first_theme_option("_PIL_PALETTE_INVERSE", {}).get("fallback_value"),
        )
        _id = template_path + image_path + str(quality) + str(use_whole_palette) + str(inverse_palette)

        def _result_callback(generated_palette: dict[str, str]) -> None:
            cls._terminal_palette_cache[_id] = generated_palette
            palette: ThemeT = {}
            palette.update(cls._terminal_palette_cache[_id])
            result_callback(palette)

        if not cls._terminal_palette_cache.get(_id):
            def generate_terminal_palette_task() -> None:
                cls._generate_terminal_palette(
                    template_path=template_path,
                    image_path=image_path,
                    quality=str(quality),
                    use_whole_palette=use_whole_palette,
                    inverse_palette=inverse_palette,
                    result_callback=_result_callback,
                )
            try:
                _app = OomoxApplicationWindow.get_instance()
                _app.disable(translate("Generating terminal palette…"))
                _app.schedule_task(generate_terminal_palette_task)
                _app.enable()
            except NoWindowError:
                generate_terminal_palette_task()
        else:
            _result_callback(cls._terminal_palette_cache[_id])
