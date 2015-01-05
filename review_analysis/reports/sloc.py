from functools import partial as _partial


from .base import Result, ReportCollection

_LINE_COUNTS = [
    'lines_diff',
    'lines_total',
    'lines_inserted',
    'lines_deleted'
]


def _size_vs(vs, df, line_count='lines_diff', limit=10000):

    if line_count not in _LINE_COUNTS:
        raise Exception(
            "Expected line_count to be done of "
            "".join(_LINE_COUNTS))

    df = df[df['revisions.totals.{0}'.format(line_count)] < limit]
    df = df[df['revisions.totals.{0}'.format(line_count)] > -limit]

    return Result(
        df,
        x='revisions.totals.{0}'.format(line_count),
        y=vs,
        kind='scatter'
    )


size_vs_reviews = _partial(_size_vs, 'labels.Code-Review.all_sets.all')
size_vs_hour = _partial(_size_vs, 'created.local.hour')
size_vs_commit_message = _partial(_size_vs, 'revisions.totals.message.length')
size_vs_comment_count = _partial(
    _size_vs, 'labels.Code-Review.all_sets.comments')

ReportCollection('sloc', [
    'revisions.totals.lines_diff',
    'revisions.totals.lines_total',
    'revisions.totals.lines_inserted',
    'revisions.totals.lines_deleted',
    'labels.Code-Review.all_sets.all',
    'created.local.hour',
    'revisions.totals.message.length',
    'labels.Code-Review.all_sets.comments',
]).add_many((
    ('size_vs_reviews', size_vs_reviews),
    ('size_vs_hour', size_vs_hour),
    ('size_vs_commit_message', size_vs_commit_message),
    ('size_vs_comment_count', size_vs_comment_count),
))
