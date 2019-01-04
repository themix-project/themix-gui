# -*- coding: utf-8 -*-
import sys
import os
import subprocess

from gi.repository import Gtk, GLib

from oomox_gui.i18n import _
from oomox_gui.plugin_api import OomoxImportPlugin, OomoxExportPlugin
from oomox_gui.export_common import FileBasedExportDialog
from oomox_gui.terminal import get_lightness
from oomox_gui.color import (
    mix_theme_colors, hex_darker, color_list_from_hex, int_list_from_hex,
)
from oomox_gui.export_common import ExportConfig

# Enable Base16 export if pystache and yaml are installed:
try:
    import pystache  # noqa  pylint: disable=unused-import
    import yaml  # noqa  pylint: disable=unused-import
except ImportError:
    print(
        "!! WARNING !! `pystache` and `python-yaml` need to be installed "
        "for exporting Base16 themes"
    )

    class PluginBase(OomoxImportPlugin):  # pylint: disable=abstract-method
        pass
else:
    class PluginBase(OomoxImportPlugin, OomoxExportPlugin):  # pylint: disable=abstract-method
        pass


if sys.version_info.minor >= 5:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from typing import List  # noqa


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


OOMOX_TO_BASE16_TRANSLATION = {
    "TERMINAL_BACKGROUND": "base00",
    "TERMINAL_FOREGROUND": "base05",

    "TERMINAL_COLOR0": "base01",
    "TERMINAL_COLOR1": "base08",
    "TERMINAL_COLOR2": "base0B",
    "TERMINAL_COLOR3": "base09",
    "TERMINAL_COLOR4": "base0D",
    "TERMINAL_COLOR5": "base0E",
    "TERMINAL_COLOR6": "base0C",
    "TERMINAL_COLOR7": "base06",

    "TERMINAL_COLOR8": "base02",
    "TERMINAL_COLOR9": "base08",  # @TODO: lighter
    "TERMINAL_COLOR10": "base0B",  # @TODO: lighter
    "TERMINAL_COLOR11": "base0A",
    "TERMINAL_COLOR12": "base0D",  # @TODO: lighter
    "TERMINAL_COLOR13": "base0E",  # @TODO: lighter
    "TERMINAL_COLOR14": "base0C",  # @TODO: lighter
    "TERMINAL_COLOR15": "base07",

    # 03, 04, 0F  -- need to be generated from them on back conversion
}


def convert_oomox_to_base16(colorscheme):
    base16_theme = {}

    base16_theme["scheme-name"] = base16_theme["scheme-author"] = \
        colorscheme["NAME"]
    base16_theme["scheme-slug"] = base16_theme["scheme-name"].split('/')[-1].lower()

    for oomox_key, base16_key in OOMOX_TO_BASE16_TRANSLATION.items():
        base16_theme[base16_key] = colorscheme[oomox_key]

    base16_theme['base03'] = mix_theme_colors(
        base16_theme['base00'], base16_theme['base05'], 0.5
    )

    if get_lightness(base16_theme['base01']) > get_lightness(base16_theme['base00']):
        base16_theme['base04'] = hex_darker(base16_theme['base00'], 20)
    else:
        base16_theme['base04'] = hex_darker(base16_theme['base00'], -20)

    base16_theme['base0F'] = hex_darker(mix_theme_colors(
        base16_theme['base08'], base16_theme['base09'], 0.5
    ), 20)

    return base16_theme


def convert_base16_to_template_data(base16_theme):
    base16_data = {}
    for key, value in base16_theme.items():
        if not key.startswith('base'):
            base16_data[key] = value
            continue

        hex_key = key + '-hex'
        base16_data[hex_key] = value
        base16_data[hex_key + '-r'], \
            base16_data[hex_key + '-g'], \
            base16_data[hex_key + '-b'] = \
            color_list_from_hex(value)

        rgb_key = key + '-rgb'
        base16_data[rgb_key + '-r'], \
            base16_data[rgb_key + '-g'], \
            base16_data[rgb_key + '-b'] = \
            int_list_from_hex(value)

        dec_key = key + '-dec'
        base16_data[dec_key + '-r'], \
            base16_data[dec_key + '-g'], \
            base16_data[dec_key + '-b'] = \
            [
                channel/255 for channel in int_list_from_hex(value)
            ]
    return base16_data


def render_base16_template(template_path, base16_theme):
    with open(template_path) as template_file:
        template = template_file.read()
    base16_data = convert_base16_to_template_data(base16_theme)
    result = pystache.render(template, base16_data)
    return result


class ConfigKeys:
    last_app = 'last_app'
    last_variant = 'last_variant'


class Base16ExportDialog(FileBasedExportDialog):

    available_apps = []  # type: List[str]
    current_app = None
    available_variants = []  # type: List[str]
    current_variant = None
    templates_dir = None
    templates_homepages = None

    _variants_changed_signal = None

    def _get_app_template_dir(self):
        return os.path.join(
            self.templates_dir, self.current_app, 'templates',
        )

    def _get_app_variant_template_path(self):
        return os.path.join(
            self._get_app_template_dir(), self.current_variant + '.mustache'
        )

    def _get_app_config(self):
        config_path = os.path.join(
            self._get_app_template_dir(), 'config.yaml'
        )
        with open(config_path) as config_file:
            config = yaml.load(config_file.read())
        return config

    def base16_stuff(self):
        # NAME
        base16_theme = convert_oomox_to_base16(self.colorscheme)
        variant_config = self._get_app_config()[self.current_variant]
        output_name = 'oomox-{}{}'.format(
            base16_theme['scheme-slug'], variant_config['extension']
        )
        output_path = os.path.join(
            variant_config['output'], output_name
        )
        print(output_path)

        # RENDER
        template_path = self._get_app_variant_template_path()
        result = render_base16_template(template_path, base16_theme)

        # OUTPUT
        self.set_text(result)
        self.show_text()

        self.export_config.save()

    def _set_variant(self, variant):
        self.current_variant = \
            self.export_config[ConfigKeys.last_variant] = \
            variant

    def _on_app_changed(self, apps_dropdown):
        self.current_app = \
            self.export_config[ConfigKeys.last_app] = \
            self.available_apps[apps_dropdown.get_active()]

        config = self._get_app_config()
        self.available_variants = list(config.keys())
        if self._variants_changed_signal:
            self._variants_dropdown.disconnect(self._variants_changed_signal)
        self._variants_store.clear()
        for variant in self.available_variants:
            self._variants_store.append([variant, ])
        self._variants_changed_signal = \
            self._variants_dropdown.connect("changed", self._on_variant_changed)

        variant = self.current_variant or self.export_config[ConfigKeys.last_variant]
        if not variant or variant not in self.available_variants:
            variant = self.available_variants[0]
        self._set_variant(variant)

        self._variants_dropdown.set_active(self.available_variants.index(self.current_variant))

        url = self.templates_homepages.get(self.current_app)
        self._homepage_button.set_sensitive(bool(url))

    def _init_apps_dropdown(self):
        options_store = Gtk.ListStore(str)
        for app_name in self.available_apps:
            options_store.append([app_name, ])
        self._apps_dropdown = Gtk.ComboBox.new_with_model(options_store)
        renderer_text = Gtk.CellRendererText()
        self._apps_dropdown.pack_start(renderer_text, True)
        self._apps_dropdown.add_attribute(renderer_text, "text", 0)

        self._apps_dropdown.connect("changed", self._on_app_changed)
        GLib.idle_add(
            self._apps_dropdown.set_active,
            (self.available_apps.index(self.current_app))
        )

    def _on_variant_changed(self, variants_dropdown):
        variant = self.available_variants[variants_dropdown.get_active()]
        self._set_variant(variant)
        self.base16_stuff()

    def _init_variants_dropdown(self):
        self._variants_store = Gtk.ListStore(str)
        self._variants_dropdown = Gtk.ComboBox.new_with_model(self._variants_store)
        renderer_text = Gtk.CellRendererText()
        self._variants_dropdown.pack_start(renderer_text, True)
        self._variants_dropdown.add_attribute(renderer_text, "text", 0)

    def _on_homepage_button(self, _button):
        url = self.templates_homepages[self.current_app]
        cmd = ["xdg-open", url, ]
        subprocess.Popen(cmd)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            height=800, width=800,
            headline=_("Base16 Export Options…"),
            **kwargs
        )
        self.label.set_text(_("Choose export options below and copy-paste the result."))
        self.export_config = ExportConfig(
            config_name='base16',
            default_config={
                ConfigKeys.last_variant: None,
                ConfigKeys.last_app: None,
            }
        )

        self.templates_dir = os.path.abspath(
            os.path.join(PLUGIN_DIR, 'base16_mirror/templates')
        )
        templates_index_path = self.templates_dir + '.yaml'
        with open(templates_index_path) as templates_index_file:
            self.templates_homepages = yaml.load(templates_index_file.read())

        # APPS
        self.available_apps = sorted(os.listdir(self.templates_dir))
        self.current_app = self.export_config[ConfigKeys.last_app]
        if not self.current_app:
            self.current_app = self.export_config[ConfigKeys.last_app] = self.available_apps[0]

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        apps_label = Gtk.Label(label=_('_Application:'), use_underline=True)
        self._init_apps_dropdown()
        apps_label.set_mnemonic_widget(self._apps_dropdown)
        hbox.add(apps_label)
        hbox.add(self._apps_dropdown)

        # VARIANTS
        variant_label = Gtk.Label(label=_('_Variant:'), use_underline=True)
        self._init_variants_dropdown()
        variant_label.set_mnemonic_widget(self._variants_dropdown)
        hbox.add(variant_label)
        hbox.add(self._variants_dropdown)

        # HOMEPAGE
        self._homepage_button = Gtk.Button(label=_('Open _Homepage'), use_underline=True)
        self._homepage_button.connect('clicked', self._on_homepage_button)
        hbox.add(self._homepage_button)

        self.options_box.add(hbox)
        self.box.add(self.options_box)
        self.options_box.show_all()


class Plugin(PluginBase):

    name = 'base16'
    display_name = 'Base16'
    export_text = 'Base16-Based Templates…'
    import_text = 'From Base16 YML Format'
    file_extensions = ('.yml', '.yaml', )
    plugin_theme_dir = os.path.abspath(
        os.path.join(PLUGIN_DIR, 'base16_mirror/schemes')
    )

    export_dialog = Base16ExportDialog

    theme_model_import = [
        {
            'display_name': _('Base16 Import Options'),
            'type': 'separator',
            'value_filter': {
                'FROM_PLUGIN': name,
            },
        },
        {
            'key': 'BASE16_GENERATE_DARK',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Inverse GUI Variant'),
            'reload_theme': True,
        },
        {
            'key': 'BASE16_INVERT_TERMINAL',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Inverse Terminal Colors'),
            'reload_theme': True,
        },
        {
            'key': 'BASE16_MILD_TERMINAL',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Mild Terminal Colors'),
            'reload_theme': True,
        },
        {
            'display_name': _('Edit Imported Theme'),
            'type': 'separator',
            'value_filter': {
                'FROM_PLUGIN': name,
            },
        },
    ]

    default_theme = {
        "TERMINAL_THEME_MODE": "manual",
    }
    translation_common = {}
    translation_common.update(OOMOX_TO_BASE16_TRANSLATION)
    translation_light = {
        "BG": "base05",
        "FG": "base00",
        "HDR_BG": "base04",
        "HDR_FG": "base01",
        "SEL_BG": "base0D",
        "SEL_FG": "base00",
        "ACCENT_BG": "base0D",
        "TXT_BG": "base06",
        "TXT_FG": "base01",
        "BTN_BG": "base03",
        "BTN_FG": "base07",
        "HDR_BTN_BG": "base05",
        "HDR_BTN_FG": "base01",

        "ICONS_LIGHT_FOLDER": "base0C",
        "ICONS_LIGHT": "base0C",
        "ICONS_MEDIUM": "base0D",
        "ICONS_DARK": "base03",
    }
    translation_dark = {
        "BG": "base01",
        "FG": "base06",
        "HDR_BG": "base00",
        "HDR_FG": "base05",
        "SEL_BG": "base0E",
        "SEL_FG": "base00",
        "ACCENT_BG": "base0E",
        "TXT_BG": "base02",
        "TXT_FG": "base07",
        "BTN_BG": "base00",
        "BTN_FG": "base05",
        "HDR_BTN_BG": "base01",
        "HDR_BTN_FG": "base05",

        "ICONS_LIGHT_FOLDER": "base0D",
        "ICONS_LIGHT": "base0D",
        "ICONS_MEDIUM": "base0E",
        "ICONS_DARK": "base00",
    }
    translation_terminal_inverse = {
        "TERMINAL_BACKGROUND": "base06",
        "TERMINAL_FOREGROUND": "base01",
    }
    translation_terminal_mild = {
        "TERMINAL_COLOR8": "base01",
        "TERMINAL_COLOR15": "base06",
        "TERMINAL_BACKGROUND": "base07",
        "TERMINAL_FOREGROUND": "base02",
    }
    translation_terminal_mild_inverse = {
        "TERMINAL_COLOR8": "base01",
        "TERMINAL_COLOR15": "base06",
        "TERMINAL_BACKGROUND": "base02",
        "TERMINAL_FOREGROUND": "base07",
    }

    def read_colorscheme_from_path(self, preset_path):
        from oomox_gui.theme_model import THEME_MODEL_BY_KEY

        base16_theme = {}
        with open(preset_path) as preset_file:
            for line in preset_file.readlines():
                try:
                    key, value, *_rest = line.split()
                    key = key.rstrip(':')
                    value = value.strip('\'"').lower()
                    base16_theme[key] = value
                except Exception:
                    pass

        oomox_theme = {}
        oomox_theme.update(self.default_theme)
        translation = {}
        translation.update(self.translation_common)

        if THEME_MODEL_BY_KEY.get('BASE16_GENERATE_DARK', {}).get('fallback_value'):
            translation.update(self.translation_dark)
        else:
            translation.update(self.translation_light)

        if THEME_MODEL_BY_KEY.get('BASE16_INVERT_TERMINAL', {}).get('fallback_value'):
            translation.update(self.translation_terminal_inverse)

        if THEME_MODEL_BY_KEY.get('BASE16_MILD_TERMINAL', {}).get('fallback_value'):
            if THEME_MODEL_BY_KEY.get('BASE16_INVERT_TERMINAL', {}).get('fallback_value'):
                translation.update(self.translation_terminal_mild)
            else:
                translation.update(self.translation_terminal_mild_inverse)

        for oomox_key, base16_key in translation.items():
            if base16_key in base16_theme:
                oomox_theme[oomox_key] = base16_theme[base16_key]
        return oomox_theme
