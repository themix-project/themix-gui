import os
import sys
import importlib


def mkdir_p(path):
    if os.path.isdir(path):
        return
    os.makedirs(path)


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path, followlinks=True) for file in files[2]
    ]


def get_plugin_module(name, path):
    if sys.version_info.minor >= 5:
        spec = importlib.util.spec_from_file_location(name, path)  # pylint: disable=no-member
        module = importlib.util.module_from_spec(spec)  # pylint: disable=no-member
        spec.loader.exec_module(module)
    else:
        loader = importlib.machinery.SourceFileLoader(name, path)
        module = loader.load_module()  # pylint: disable=deprecated-method,no-value-for-parameter
    return module
