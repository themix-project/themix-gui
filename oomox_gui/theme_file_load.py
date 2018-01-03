import subprocess

from .config import colors_dir, FALLBACK_COLOR
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


def read_colorscheme_from_path(preset_path):
    theme_keys = [item['key'] for item in theme_model if 'key' in item]

    # @TODO: remove legacy stuff (using bash logic inside the themes)
    theme_keys.append('NOGUI')
    colorscheme = {}
    with open(preset_path) as f:
        for line in f.readlines():
            parsed_line = line.strip().split('=')
            key = parsed_line[0]
            try:
                if not key.startswith("#"):
                    if key in theme_keys:
                        colorscheme[key] = parsed_line[1]
            # ignore unparseable lines:
            except IndexError:
                pass

    # migration workaround:
    if colorscheme.get('NOGUI'):
        colorscheme = bash_preprocess(preset_path)

    for theme_value in theme_model:
        key = theme_value.get('key')
        if not key:
            continue
        fallback_key = theme_value.get('fallback_key')
        fallback_value = theme_value.get('fallback_value')
        value = colorscheme.get(key)
        if value is None and (fallback_key or fallback_value is not None):
            if fallback_value is not None:
                value = colorscheme[key] = fallback_value
            else:
                value = colorscheme[key] = colorscheme[fallback_key]

        if value is None and fallback_value is False:
            colorscheme[key] = FALLBACK_COLOR
        # migration workaround #2: resolve color links
        elif isinstance(value, str) and value.startswith("$"):
            try:
                colorscheme[key] = colorscheme[value.lstrip("$")]
            except KeyError:
                colorscheme[key] = FALLBACK_COLOR

        value_type = theme_value['type']
        if value_type == 'bool':
            if isinstance(value, str):
                colorscheme[key] = str_to_bool(value)
        elif value_type == 'int':
            colorscheme[key] = int(value)
        elif value_type == 'float':
            colorscheme[key] = float(value)

    return colorscheme


def read_colorscheme_from_preset(preset_name):
    return read_colorscheme_from_path(os.path.join(colors_dir, preset_name))


