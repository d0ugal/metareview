from __future__ import print_function

from hashlib import sha1
from os import path, makedirs, unlink

from json import load, loads


_PATH = path.join(path.abspath(path.dirname(__file__)), '..', '..', '_cache')

GERRIT_MAGIC_JSON_PREFIX = b")]}\'\n"


def _ensure_directory(directory):
    if not path.exists(directory):
        makedirs(directory)


def _cache_path(key):
    padded = "0000" + key
    part_key = padded[-4:-2], padded[-2:]
    cache_dir = path.join(_PATH, "/".join(part_key))
    cache_path = path.join(_PATH, cache_dir, f'{key}.json')
    return cache_dir, cache_path


def is_saved(key):
    cd, cp = _cache_path(key)
    if path.exists(cp):
        with open(cp) as cached_file:
            try:
                json = load(cached_file)
                if not json:
                    unlink(cp)
                return json
            except Exception:
                raise Exception("Invalid JSON cached:", cached_file)
        return json


def save(key, contents):
    cd, cp = _cache_path(key)
    contents = contents.encode('utf-8')

    if contents.startswith(GERRIT_MAGIC_JSON_PREFIX):
        contents = contents[len(GERRIT_MAGIC_JSON_PREFIX):]

    json = loads(contents.decode())

    if json:
        _ensure_directory(cd)
        with open(cp, 'wb+') as cache_file:
            cache_file.write(contents)
    else:
        print(key, "Not caching empty result...")

    return json
