from __future__ import print_function

from hashlib import sha1
from os import path, makedirs, unlink

from json import load, loads


_PATH = path.join(path.abspath(path.dirname(__file__)), '..', '_cache')

GERRIT_MAGIC_JSON_PREFIX = b")]}\'\n"


def get_or_call(url, func, cache_only=False):

    key = unique_alphanum(url)
    part_key = key[:2]
    cache_dir = path.join(_PATH, "/".join(part_key))
    cache_path = path.join(_PATH, "/".join(part_key), key)

    if path.exists(cache_path):
        with open(cache_path) as cached_file:
            try:
                json = load(cached_file)
                if not json:
                    unlink(cache_path)
                return json
            except Exception:
                raise Exception("Invalid JSON cached:", cached_file)
    elif cache_only:
        return []

    result = func(url)
    content = result.text.encode('utf-8')

    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        content = content[len(GERRIT_MAGIC_JSON_PREFIX):]

    ensure_directory(cache_dir)

    json = loads(content.decode())

    if json:
        with open(cache_path, 'wb+') as cache_file:
            cache_file.write(content)
    else:
        print("Not caching empty result...")

    return json


def unique_alphanum(string):
    return str(sha1(string.encode("utf-8")).hexdigest())[:8]


def ensure_directory(directory):
    if not path.exists(directory):
        makedirs(directory)
