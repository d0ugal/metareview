from __future__ import print_function

from itertools import count
import time

from metareview.utils import cache


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

    def __init__(self, start=1, end=None):
        self.start = start
        self.end = end

    def _get(self, key, url):
        cached = cache.is_saved(key)
        if cached:
            return cached
        return []

    def url_generator(self):
        for i in count(start=self.start):
            if self.end is not None and i > self.end:
                break
            yield str(i), CHANGES_URL.format(i)

    def reviews(self):
        for key, url in self.url_generator():
            reviews = self._get(key, url)
            for review in reviews:
                if review:
                    yield review
