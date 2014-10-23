from datetime import timedelta
from itertools import islice
import re

from pandas import DataFrame, to_datetime
from pygerrit.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from requests.exceptions import SSLError
from retrying import retry

from review_analysis.util import (get_or_call, CacheMiss, flatten,
                                  unique_alphanum)

STATUSES = ['merged', 'new', 'submitted', 'abandoned', 'draft']

CHANGES_URL = ("/changes/?q=status:%s"
               "&o=ALL_COMMITS"
               "&o=ALL_FILES"
               "&o=ALL_REVISIONS"
               "&o=DETAILED_ACCOUNTS"
               "&o=DETAILED_LABELS"
               "&o=DOWNLOAD_COMMANDS"
               "&o=MESSAGES"
               "&n=50")

MERGERS = (
    1,  # corvus
    3,  # jenkins
)
CI = (
    3,  # Jenkins
    7677,  # hyper-v-ci
    9578,  # turbo-hipster
    9008,  # vmwareminesweeper
    10118,  # powerkvm
    10385,  # citrix_xenserver_ci
)


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

        self.modifiers = [dates, project_group, label_totals,
                          messages_metadata, latest_revision, merged_details,
                          local_times]

    @retry(
        stop_max_attempt_number=5,
        retry_on_exception=lambda e: isinstance(e, SSLError)
    )
    def _get(self, url):
        try:
            if self.verbose:
                print url
            return get_or_call('gerrit-get/{0}'.format(self._url_key),
                               url, self.gerrit.get, self.cache_only)
        except CacheMiss:
            return []

    def modify(self, review):
        for modifier in self.modifiers:
            modifier(review)
        return review

    def reviews(self):

        for status in STATUSES:

            url = CHANGES_URL % status
            original = url

            while url is not None:

                review = {}

                for review in self._get(url):
                    if review.get('_number') is None:
                        print review
                    yield self.modify(review)

                if review.get('_more_changes') is not None:
                    url = "%s&N=%s" % (original, review['_sortkey'])
                else:
                    url = None

    def as_dataframe(self, limit=None):

        reviews = (dict(flatten(_)) for _ in self.reviews())

        if limit is not None:
            reviews = islice(reviews, limit)

        df = DataFrame.from_records(reviews)

        df = df.set_index('_number')

        return df

    def reviewers(self):
        """
        Rather than return a list of reviews.
        """


def project_group(review):
    """
    Given a review, extrapolate the project group from the project name
    """
    review['project.group'] = review['project'].split('/')[0]


def label_totals(review):
    """
    Go through the review labels and add totals.
    """

    def _filter(hay, needle):
        return [_ for _ in hay if _.get('value') == needle
                and _.get('account_id') not in CI]

    def _count(hay, needle):
        return len(_filter(hay, needle))

    if 'Code-Review' in review['labels']:
        cr = review['labels']['Code-Review'].get('all', {})
        review_totals = {}
        review_totals['+2'] = _count(cr, 2)
        review_totals['+1'] = _count(cr, 1)
        review_totals['0'] = _count(cr, 0)
        review_totals['-1'] = _count(cr, -1)
        review_totals['-2'] = _count(cr, -2)
        review_totals['all'] = len(cr)
        review['labels']['Code-Review']['totals'] = review_totals

    if 'Verified' in review['labels']:
        cr = review['labels']['Verified'].get('all', {})
        review_verified = {}
        review_verified['+2'] = _count(cr, 2)
        review_verified['+1'] = _count(cr, 1)
        review_verified['0'] = _count(cr, 0)
        review_verified['-1'] = _count(cr, -1)
        review_verified['-2'] = _count(cr, -2)
        review_verified['all'] = len(cr)
        review['labels']['Verified']['totals'] = review_verified

    if 'Workflow' in review['labels']:
        cr = review['labels']['Workflow'].get('all', {})
        review_workflow = {}
        review_workflow['+1'] = _count(cr, 1)
        review_workflow['0'] = _count(cr, 0)
        review_workflow['-1'] = _count(cr, -1)
        review_workflow['all'] = len(cr)
        review['labels']['Workflow']['totals'] = review_workflow


MESSAGE_PATCH_SET = re.compile(r'^Patch Set (?P<patch_set>\d+):')
MESSAGE_REVIEW = re.compile(r'Code-Review(?P<review>[\+\-]{1}\d+)')
MESSAGE_REMOVED = re.compile(r'\-Code-Review')
MESSAGE_COMMENTS = re.compile(r'\((?P<count>\d+) comment(s)?\)')


def messages_metadata(review):
    """
    """
    if 'Code-Review' not in review['labels']:
        return

    def message_to_review(message):
        patch_sets = MESSAGE_PATCH_SET.findall(message)
        code_reviews = MESSAGE_REVIEW.findall(message)
        comments = MESSAGE_COMMENTS.findall(message)

        try:
            comments = int(comments[0][0])
        except IndexError:
            comments = 0

        if len(code_reviews) == 0:
            return

        try:
            return patch_sets[0], code_reviews[0], comments
        except IndexError:
            pass

    for message in review['messages']:

        set_review = message_to_review(message['message'])
        if set_review is None:
            continue

        patch_set, review_value, comments = set_review

        if 'all_sets' not in review['labels']['Code-Review']:
            review['labels']['Code-Review']['all_sets'] = {
                'all': 0, '-2': 0, '-1': 0, '+1': 0, '+2': 0, 'comments': 0,
            }

        review['labels']['Code-Review']['all_sets']['all'] += 1
        review['labels']['Code-Review']['all_sets'][review_value] += 1
        review['labels']['Code-Review']['all_sets']['comments'] += comments


def latest_revision(review):

    def _lines(rev, key):
        for r in rev.get('files', {}).values():
            yield r.get(key, 0)

    if len(review['revisions']) == 0:
        return

    revisions = review.pop('revisions')

    review['revisions'] = {
        "all": revisions.items()
    }

    rev_sort = lambda rev: rev[1]['_number']
    sha, latest = sorted(revisions.items(), key=rev_sort)[-1]

    totals = {}
    totals['count'] = latest['_number']

    totals['lines_inserted'] = sum(_lines(latest, 'lines_inserted'))
    totals['lines_deleted'] = sum(_lines(latest, 'lines_deleted'))
    latest.pop('files')
    review['revisions']['latest'] = latest

    totals['lines_total'] = (
        totals['lines_inserted'] + totals['lines_deleted'])
    totals['lines_diff'] = (
        totals['lines_inserted'] - totals['lines_deleted'])

    totals['message'] = latest['commit']['message']
    totals['message.length'] = len(
        latest['commit']['message'])

    review['owner']['tz'] = latest['commit']['author']['tz']

    review['revisions']['totals'] = totals


def merged_details(review):

    if review['status'] == 'MERGED':
        jenkins_messages = [
            message for message in review['messages']
            if message.get('author', {}).get('_account_id') in MERGERS
        ]

        if len(jenkins_messages):
            last_message = jenkins_messages[-1]
            review['merged.date'] = last_message['date']
            review['merged.id'] = last_message['id']


def local_times(review):

    delta = timedelta(minutes=review['owner']['tz'])

    review['created.local'] = review['created'] + delta
    review['created.year'] = review['created'].year
    review['created.month'] = review['created'].month
    review['created.hour'] = review['created'].hour
    review['created.local.hour'] = review['created.local'].hour

    if 'merged.date' in review:
        review['merged.date'] = to_datetime(review['merged.date'])
        review['merged.date.local'] = review['merged.date'] + delta
        delta = review['merged.date'] - review['created']
        seconds = delta.total_seconds()
        if seconds > 0:
            review['review_duration'] = seconds


def dates(review):

    review['created'] = to_datetime(review['created'])
    review['merged'] = to_datetime(review['created'])
