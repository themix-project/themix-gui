import subprocess

from .config import FALLBACK_COLOR
from .theme_model import theme_model
from .helpers import str_to_bool


def bash_preprocess(preset_path):
    colorscheme = {"NOGUI": True}
    theme_values_with_keys = [
        theme_value
        for theme_value in theme_model
        if theme_value.get('key')
    ]
    process = subprocess.run(
        [
            "bash", "-c",
            "source " + preset_path + " ; " +
            "".join(
                "echo ${{{}-None}} ;".format(theme_value['key'])
                for theme_value in theme_values_with_keys
            )
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.stderr:
        raise(Exception(
            "Pre-processing failed:\nstdout:\n{}\nstderr:\n{}".format(
                process.stdout, process.stderr
            )))
    lines = process.stdout.decode("UTF-8").split()
    for i, theme_value in enumerate(theme_values_with_keys):
        value = lines[i]
        if value == 'None':
            value = None
        colorscheme[theme_value['key']] = value
    return colorscheme


def parse_theme_value(theme_value, colorscheme):
    result_value = colorscheme.get(theme_value['key'])
    fallback_key = theme_value.get('fallback_key')
    fallback_value = theme_value.get('fallback_value')

    if result_value is None and (fallback_key or fallback_value is not None):
        if fallback_value is not None:
            result_value = fallback_value
        else:
            result_value = colorscheme[fallback_key]

    value_type = theme_value['type']
    if value_type == 'bool':
        if isinstance(result_value, str):
            result_value = str_to_bool(result_value)
    elif value_type == 'int':
        result_value = int(result_value)
    elif value_type == 'float':
        result_value = float(result_value)
    elif value_type == 'options':
        available_options = [option['value'] for option in theme_value['options']]
        if result_value not in available_options:
            if fallback_value in available_options:
                result_value = fallback_value
            else:
                result_value = available_options[0]

    return result_value


def read_colorscheme_from_path(preset_path):
    theme_keys = [item['key'] for item in theme_model if 'key' in item]

    # @TODO: remove legacy stuff (using bash logic inside the themes)
    theme_keys.append('NOGUI')

    colorscheme = {}
    with open(preset_path) as file_object:
        for line in file_object.readlines():
            parsed_line = line.strip().split('=')
            key = parsed_line[0]
            try:
                if not key.startswith("#"):
                    if key in theme_keys:
                        colorscheme[key] = parsed_line[1]
            # ignore unparseable lines:
            except IndexError:
                pass

    # @TODO: remove migration workaround #2:
    if colorscheme.get('NOGUI'):
        colorscheme = bash_preprocess(preset_path)

    for theme_model_item in theme_model:
        key = theme_model_item.get('key')
        if not key:
            continue
        colorscheme[key] = parse_theme_value(theme_model_item, colorscheme)

    return colorscheme
