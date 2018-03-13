import os


def mkdir_p(path):
    if os.path.isdir(path):
        return
    os.makedirs(path)


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path, followlinks=True) for file in files[2]
    ]
