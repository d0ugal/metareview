from os import path, makedirs
from hashlib import sha1
from string import letters, digits

from simplejson import load, dumps
from simplejson.scanner import JSONDecodeError


_PATH = path.join(path.abspath(path.dirname(__file__)), '..', '_cache')


class CacheMiss(Exception):
    pass


def get_or_call(cache_name, url, func, cache_only=False):

    key = unique_alphanum(url)
    cache_dir = path.join(_PATH, cache_name)
    cache_path = path.join(_PATH, cache_name, key)

    if path.exists(cache_path):
        with open(cache_path) as cached_file:
            try:
                return load(cached_file)
            except JSONDecodeError:
                raise Exception("Invalid JSON cached:", cached_file)
    elif cache_only:
        raise CacheMiss

    result = func(url)

    ensure_directory(cache_dir)

    with open(cache_path, 'w+') as cache_file:
        cache_file.write(dumps(result, sort_keys=True, indent=4 * ' '))

    return result


def unique_alphanum(string):
    digest = str(sha1(string).hexdigest())[:8]
    alphanum = letters + digits
    string = string.lower()
    cleaned = ''.join(l if l in alphanum else '-' for l in string)
    return "%s-%s" % (digest, cleaned)


def ensure_directory(directory):
    if not path.exists(directory):
        makedirs(directory)
