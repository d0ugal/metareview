from functools import wraps
from os import path, makedirs
from hashlib import md5
from simplejson import load, dumps
from simplejson.scanner import JSONDecodeError
from string import letters, digits


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

    if not path.exists(cache_dir):
        makedirs(cache_dir)

    with open(cache_path, 'w+') as cache_file:
        cache_file.write(dumps(result, sort_keys=True, indent=4 * ' '))

    return result


def file_cache(cache_name, load_json=True):
    def cache_decorator(func):
        @wraps(func)
        def func_wrapper(url):
            get_or_call(cache_name, url, func)
        return func_wrapper
    return cache_decorator


def flatten(items, current_path=None):
    """
    Given a nested data structure, create a flattened representation of it that
    can then more easily be converted into something like a CSV.

    {
        'key': 'value',
        'key2': {
            'valuea': 1,
            'valueb': 2,
        }
    }

    --->

    {
        'key': 'value',
        'key2.valuea': 1,
        'key2.valueb': 2,
    }

    """

    if isinstance(items, dict):
        items = items.iteritems()

    for key, value in items:

        if current_path is not None:
            new_path = "{0}.{1}".format(current_path, key)
        else:
            new_path = key

        if not isinstance(key, basestring):
            raise ValueError("Expect all dictionary keys to be strings.")

        if not isinstance(value, dict):
            yield new_path, value
            continue

        for sub_key, sub_value in flatten(value, new_path):
            yield sub_key, sub_value


def unique_alphanum(string):
    digest = str(md5(string).hexdigest())
    alphanum = letters + digits
    string = string.lower()
    cleaned = ''.join(l if l in alphanum else '-' for l in string)
    return "%s-%s" % (digest, cleaned)
