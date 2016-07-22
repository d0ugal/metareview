from hashlib import sha1
from os import path, makedirs

from json import load, loads


_PATH = path.join(path.abspath(path.dirname(__file__)), '..', '_cache')


class CacheMiss(Exception):
    pass

GERRIT_MAGIC_JSON_PREFIX = ")]}\'\n"


def get_or_call(url, func, cache_only=False):

    key = unique_alphanum(url.replace("https://review.openstack.org", ""))
    part_key = key[:2]
    cache_dir = path.join(_PATH, "/".join(part_key))
    cache_path = path.join(_PATH, "/".join(part_key), key)

    if path.exists(cache_path):
        with open(cache_path) as cached_file:
            try:
                return load(cached_file)
            except Exception:
                raise Exception("Invalid JSON cached:", cached_file)
    elif cache_only:
        raise CacheMiss

    result = func(url)
    content = result.text.encode('utf-8')

    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        content = content[len(GERRIT_MAGIC_JSON_PREFIX):]

    ensure_directory(cache_dir)

    with open(cache_path, 'w+') as cache_file:
        cache_file.write(content)

    return loads(content)


def unique_alphanum(string):
    return str(sha1(string).hexdigest())[:8]


def ensure_directory(directory):
    if not path.exists(directory):
        makedirs(directory)
