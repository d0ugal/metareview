from __future__ import print_function

from itertools import count
import time

from retrace import retry
import requests

from metareview.util import (get_or_call, unique_alphanum)


CHANGES_URL = ("https://review.openstack.org"
               "/changes/?q={}"
               "&o=ALL_COMMITS"
               "&o=ALL_FILES"
               "&o=ALL_REVISIONS"
               "&o=DETAILED_ACCOUNTS"
               "&o=DETAILED_LABELS"
               "&o=DOWNLOAD_COMMANDS"
               "&o=MESSAGES")


class Gerrit(object):

    def __init__(self, cache_only=False, verbose=False, start=1, end=None):
        self.url = 'https://review.openstack.org'
        self._url_key = unique_alphanum(self.url)
        self.start = start
        self.end = end
        self.verbose = verbose
        self.cache_only = cache_only
        self.gerrit = requests.get

    @retry(limit=20, interval=time.sleep)
    def _get(self, url):
        return get_or_call(url, self.gerrit, self.cache_only)

    def _url_generator(self):
        for i in count(start=self.start):
            print(i)
            if self.end is not None and i > self.end:
                break
            yield CHANGES_URL.format(i)

    def reviews(self):
        for url in self._url_generator():
            reviews = self._get(url)
            for review in reviews:
                yield review
