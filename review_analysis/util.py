from functools import wraps
from os import path, makedirs
from hashlib import sha1
from string import letters, digits
from textwrap import dedent as tw_dedent
from datetime import date, datetime

from pandas.tslib import Timestamp

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

    if not path.exists(cache_dir):
        makedirs(cache_dir)

    with open(cache_path, 'w+') as cache_file:
        cache_file.write(dumps(result, sort_keys=True, indent=4 * ' '))

    return result


def file_cache(cache_name):
    def cache_decorator(func):
        @wraps(func)
        def func_wrapper(url):
            return get_or_call(cache_name, url, func)
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
    digest = str(sha1(string).hexdigest())[:8]
    alphanum = letters + digits
    string = string.lower()
    cleaned = ''.join(l if l in alphanum else '-' for l in string)
    return "%s-%s" % (digest, cleaned)


def dedent(text):
    if text is None:
        return
    return tw_dedent(text).strip()


def encode_conplex(obj):

    if isinstance(obj, Timestamp):
        return obj.to_datetime().isoformat()

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError(repr(obj) + " is not JSON serializable")
