import importlib
import os
import re
import sys


def mkdir_p(path):
    if os.path.isdir(path):
        return
    os.makedirs(path)


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path, followlinks=True) for file in files[2]
    ]


def get_plugin_module(name, path, submodule=None):
    if sys.version_info.minor < 5:
        raise RuntimeError('Python 3.5+ is required')
    spec = importlib.util.spec_from_file_location(name, path)  # pylint: disable=no-member
    module = importlib.util.module_from_spec(spec)  # pylint: disable=no-member
    spec.loader.exec_module(module)
    if submodule:
        return getattr(module, submodule)
    return module


def apply_chain(func, *args_args):
    result = func
    for args in args_args:
        result = result(*args)
    return result


def call_method_from_class(klass, klass_args, method_name, method_args):
    return getattr(klass(*klass_args), method_name)(*method_args)


def delayed_partial(func, delayed_args, rest_args):
    computed_args = []
    for delayed_func, args in delayed_args:
        computed_args.append(delayed_func(*args))
    all_args = computed_args + list(rest_args)
    return func(*all_args)


def natural_sort(list_to_sort):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(list_to_sort, key=alphanum_key)
