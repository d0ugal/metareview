from itertools import count
import time

from httplib import IncompleteRead
from pygerrit.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from requests.exceptions import SSLError
from retrace import retry
import requests

from review_analysis.util import (get_or_call, CacheMiss, unique_alphanum)

CHANGES_URL = ("/changes/?q={}"
               "&o=ALL_COMMITS"
               "&o=ALL_FILES"
               "&o=ALL_REVISIONS"
               "&o=DETAILED_ACCOUNTS"
               "&o=DETAILED_LABELS"
               "&o=DOWNLOAD_COMMANDS"
               "&o=MESSAGES")


class Gerrit(object):

    def __init__(self, username, password, url, cache_only=False,
                 verbose=False):

        self.username = username
        self.password = password
        self.url = url

        self._url_key = unique_alphanum(self.url)

        self.verbose = verbose

        self.cache_only = cache_only

        auth = HTTPDigestAuth(self.username, self.password)
        self.gerrit = GerritRestAPI(url=self.url, auth=auth)

    @retry(
        on_exception=(
            SSLError, IncompleteRead, requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError
        ),
        limit=10,
        interval=time.sleep
    )
    def _get(self, url):

        try:
            if self.verbose:
                print url
            return get_or_call(url, self.gerrit.get, self.cache_only)
        except CacheMiss:
            return None

    def _url_generator(self):

        for i in count(start=1):
            yield CHANGES_URL.format(i)

    def reviews(self):
        for url in self._url_generator():
            reviews = self._get(url)
            for review in reviews:
                yield review
