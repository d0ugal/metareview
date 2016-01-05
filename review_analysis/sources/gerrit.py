from itertools import count
import datetime

from httplib import IncompleteRead
from pygerrit.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from requests.exceptions import SSLError
from retrying import retry
import requests

from review_analysis.util import (get_or_call, CacheMiss, unique_alphanum)

STATUSES = ['merged', 'new', 'submitted', 'abandoned', 'draft']

BATCH_SIZE = 500

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
        stop_max_attempt_number=5,
        retry_on_exception=lambda e: isinstance(e, (
            SSLError, IncompleteRead, requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError)),
        wait_exponential_multiplier=1000, wait_exponential_max=10000
    )
    def _get(self, url):
        try:
            if self.verbose:
                print datetime.datetime.now(), url,
            return get_or_call('gerrit-get/{0}'.format(self._url_key),
                               url, self.gerrit.get, self.cache_only)
        except CacheMiss:
            return []
        finally:
            if self.verbose:
                print datetime.datetime.now()

    def reviews(self):

        for status in STATUSES:

            for i in count():

                url = CHANGES_URL % (status, BATCH_SIZE, i * BATCH_SIZE)
                review = {}

                for review in self._get(url):
                    yield review

                if review.get('_more_changes') is None:
                    break

    def reviews_es_bulk_format(self):

        for review in self.reviews():

            yield {
                '_index': 'review',
                '_type': 'review-openstack-org',
                '_id': review['id'],
                '_source': review
            }
