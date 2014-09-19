from collections import Counter
from hashlib import md5
from os import environ, path
import re

from pygerrit.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from retrying import retry
from simplejson import dumps, loads

STATUSES = ['merged', 'new', 'submitted', 'abandoned', 'draft']

CHANGES_URL = ("/changes/?q=status:%s"
               "&o=ALL_REVISIONS"
               "&o=DETAILED_ACCOUNTS"
               "&o=ALL_FILES"
               "&o=ALL_COMMITS"
               "&o=DETAILED_LABELS"
               "&o=MESSAGES"
               "&n=500")

MERGERS = (
    1,          # corvus
    3,          # jenkins
)

CI = (
    3,          # Jenkins
    7677,       # hyper-v-ci
    9578,       # turbo-hipster
    9008,       # vmwareminesweeper
    10118,      # powerkvm
    10385,      # citrix_xenserver_ci
)


def _filter(hay, needle):
    return [_ for _ in hay
            if _.get('value') == needle
            and _.get('account_id') not in CI]


def _count(hay, needle):
    return len(_filter(hay, needle))

EXTENSIONS = [
    'py', 'xml', 'json', 'rst', 'html', 'pp', 'txt', 'css', 'js', 'yaml',
    'conf', 'ini', 'sh', 'rb', 'php'
]

MESSAGE_PATCH_SET = re.compile(r'^Patch Set (?P<patch_set>\d+):')
MESSAGE_REVIEW = re.compile(r'Code-Review(?P<review>[\+\-]{1}\d+)')
MESSAGE_REMOVED = re.compile(r'\-Code-Review')
MESSAGE_COMMENTS = re.compile(r'\((?P<count>\d+) comment(s)?\)')


def _lines_by_lang(rev, key):

    c = Counter()

    for filename, count in rev.get('files', {}).iteritems():
        extension = filename.rsplit('.', 1)[-1].lower()

        if extension not in EXTENSIONS:
            extension = 'other'

        c[extension] += count.get(key, 0)

    return c


def _lines(rev, key):
    for r in rev.get('files', {}).values():
        yield r.get(key, 0)


def _company(email):
    return email.rsplit('@', 1)[-1].lower()


def message_to_review(message):

    patch_sets = MESSAGE_PATCH_SET.findall(message)
    code_reviews = MESSAGE_REVIEW.findall(message)
    review_removed = MESSAGE_REMOVED.findall(message)
    comments = MESSAGE_COMMENTS.findall(message)

    try:
        comments = int(comments[0][0])
    except IndexError:
        comments = 0

    if len(code_reviews) == 0 and 'Code-Review' in message and len(review_removed) != 1:
        return

    if len(patch_sets) == 0:
        return
    elif len(patch_sets) > 1:
        print "1"
        return

    if len(set(code_reviews)) > 1:
        print "2"
        return

    if len(review_removed) > 1:
        print "3"
        return

    if len(code_reviews) > 0 and len(review_removed) > 0:
        print "4"
        return

    if len(code_reviews) == 1:
        review = code_reviews[0]
    elif len(review_removed) == 1:
        return
    else:
        return

    return patch_sets[0], review, comments


class StatClient(object):

    def __init__(self, username=None, password=None, url=None):

        if username is not None:
            self.username = username
        else:
            self.username = environ.get('GERRIT_USERNAME')

        if password is not None:
            self.password = password
        else:
            self.password = environ.get('GERRIT_PASSWORD')

        if url is None:
            self.url = 'https://review.openstack.org'
        else:
            self.url = url

        auth = HTTPDigestAuth(self.username, self.password)
        self.gerrit = GerritRestAPI(url=self.url, auth=auth)

    def _process(self, review):

        # Remove rubbish.
        review.pop('permitted_labels')
        review.pop('removable_reviewers')

        owner = review.pop('owner')
        labels = review.pop('labels')
        revisions = review.pop('revisions')
        messages = review.pop('messages')

        account_id = owner['_account_id']

        review['owner.username'] = owner.get('username')
        review['owner._account_id'] = account_id
        review['owner.name'] = owner.get('name')
        review['owner.company'] = _company(owner.get('email', ''))

        review['project.group'] = review['project'].split('/')[0]

        if 'Workflow' in labels:
            wf = labels['Workflow'].get('all', {})
            review['Workflow.approved'] = _count(wf, 1)
            try:
                review['Workflow.approved.on'] = _filter(wf, 1)[0]['date']
                review['Workflow.approved.company'] = _company(_filter(
                    wf, 1)[0].get('email', ''))
            except IndexError:
                pass
            review['Workflow.none'] = _count(wf, 0)
            review['Workflow.wip'] = _count(wf, -1)
            review['Workflow.total'] = len(wf)

        if 'Verified' in labels:
            vf = labels['Verified'].get('all', {})
            review['Verified.+2'] = _count(vf, 2)
            review['Verified.+1'] = _count(vf, 1)
            review['Verified.0'] = _count(vf, 0)
            review['Verified.-1'] = _count(vf, -1)
            review['Verified.-2'] = _count(vf, -2)
            review['Verified.total'] = len(vf)

        if 'Code-Review' in labels:
            cr = labels['Code-Review'].get('all', {})
            review['Code-Review.latest.+2'] = _count(cr, 2)
            review['Code-Review.latest.+1'] = _count(cr, 1)
            review['Code-Review.latest.0'] = _count(cr, 0)
            review['Code-Review.latest.-1'] = _count(cr, -1)
            review['Code-Review.latest.-2'] = _count(cr, -2)
            review['Code-Review.total'] = len(cr)

        for message in messages:
            set_review = message_to_review(message['message'])

            if set_review is None:
                continue

            patch_set, review_value, comments = set_review

            set_key = 'Code-Review.%s.%s' % (patch_set, review_value)
            all_key = 'Code-Review.all.%s' % (review_value, )
            set_comments = 'Code-Review.%s.comments' % (patch_set, )
            all_comments = 'Code-Review.all.comments'

            for key in [set_key, all_key, set_comments, all_comments]:
                if key not in review:
                    review[key] = 0

            review[set_key] += 1
            review[all_key] += 1
            review[set_comments] += comments
            review[all_comments] += comments

        if len(revisions) > 0:
            rev_sort = lambda rev: rev['_number']
            revision = sorted(revisions.values(), key=rev_sort)[-1]
            review['revisions.count'] = revision['_number']

            review['revisions.lines_inserted'] = sum(
                _lines(revision, 'lines_inserted'))
            review['revisions.lines_deleted'] = sum(
                _lines(revision, 'lines_deleted'))

            for extension, value in _lines_by_lang(
                    revision, 'lines_inserted').iteritems():
                review['revisions.lines_inserted.%s' % extension] = value
            for extension, value in _lines_by_lang(
                    revision, 'lines_deleted').iteritems():
                review['revisions.lines_deleted.%s' % extension] = value

            review['revisions.lines_total'] = (
                review['revisions.lines_inserted'] +
                review['revisions.lines_deleted'])

            review['revisions.commit.message'] = revision['commit']['message']
            review['revisions.commit.message.length'] = len(
                revision['commit']['message'])

            review['owner.tz'] = revision['commit']['author']['tz']

        if review['status'] == 'MERGED':
            jenkins_messages = [
                message for message in messages
                if message.get('author', {}).get('_account_id') in MERGERS
            ]

            if len(jenkins_messages):
                last_message = jenkins_messages[-1]
                review['merged.date'] = last_message['date']
                review['merged.id'] = last_message['id']

        types = set(map(type, review.values()))
        if not types.issubset({list, int, str, unicode, None.__class__, bool}):
            print types
            print review
            raise Exception()

        return review

    @retry(stop_max_attempt_number=5)
    def _get_url(self, url):
        return self.gerrit.get(url)

    def get_url(self, url, cache_only=False):

        p = "parsed/%s.json" % (str(md5(url).hexdigest()))

        if path.exists(p):
            with open(p) as parsed_cache:
                try:
                    for review in loads(parsed_cache.read()):
                        yield review
                except:
                    print p
                    raise
            raise StopIteration
        elif cache_only:
            raise StopIteration

        f = "data/%s.json" % (str(md5(url).hexdigest()))

        if path.exists(f):
            with open(f) as file_cache:
                try:
                    data = loads(file_cache.read())
                except:
                    print f
                    raise
        else:
            data = self._get_url(url)
            with open(f, 'w+') as file_cache:
                file_cache.write(dumps(data, sort_keys=True, indent=4 * ' '))

        flattened_data = []
        for review in data:
            review = self._process(review)
            flattened_data.append(review)
            yield review

        json = dumps(flattened_data, sort_keys=True, indent=4 * ' ')
        with open(p, 'w+') as parsed_cache:
            parsed_cache.write(json)

    def reviews(self, cache_only=False):

        for status in STATUSES:

            url = CHANGES_URL % status

            while url is not None:

                review = {'_more_changes': None}
                for review in self.get_url(url, cache_only):
                    yield review

                if review.get('_more_changes'):
                    url = "%s&N=%s" % (url, review['_sortkey'])
                else:
                    url = None
