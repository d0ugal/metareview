from itertools import count
import datetime
import time

from httplib import IncompleteRead
from pygerrit.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from requests.exceptions import SSLError
from retrace import retry
import requests

from review_analysis.util import (get_or_call, CacheMiss, unique_alphanum)

STATUSES = ['merged', 'new', 'submitted', 'abandoned', 'draft']

BATCH_SIZE = 50

CHANGES_URL = ("/changes/?q=status:%s"
               "&o=ALL_COMMITS"
               "&o=ALL_FILES"
               "&o=ALL_REVISIONS"
               "&o=DETAILED_ACCOUNTS"
               "&o=DETAILED_LABELS"
               "&o=DOWNLOAD_COMMANDS"
               "&o=MESSAGES"
               "&n=%s"
               "&start=%s")


class Gerrit(object):

    def __init__(self, username, password, url,
                 cache_only=False, verbose=False):

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

        start = datetime.datetime.now()

        try:
            if self.verbose:
                print start, url,
            return get_or_call('gerrit-get/{0}'.format(self._url_key),
                               url, self.gerrit.get, self.cache_only)
        except CacheMiss:
            return []
        finally:
            if self.verbose:
                print (datetime.datetime.now() - start).seconds

    def _url_generator(self):

        for status in STATUSES:
            for i in count():
                url = CHANGES_URL % (status, BATCH_SIZE, i * BATCH_SIZE)
                yield url

    def reviews(self):

        for url in self._url_generator():

            review = {}

            for review in self._get(url):
                yield review

            if review.get('_more_changes') is None:
                break
