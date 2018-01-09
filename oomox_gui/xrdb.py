import subprocess


class XrdbCache(object):

    _cache = None

    @classmethod
    def get(cls):
        if cls._cache:
            return cls._cache

        timeout = 10
        command = ['xrdb', '-query']

        result = {}
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for line in iter(proc.stdout.readline, b''):
            line = line.decode("utf-8")
            key, value, *rest = line.split(':')
            key = key.lstrip('*').lstrip('.')
            value = value.strip()
            result[key] = value
        proc.communicate(timeout=timeout)
        if proc.returncode == 0:
            cls._cache = result
            return result
        print('xrdb not found')

    @classmethod
    def clear(cls):
        cls._cache = None
