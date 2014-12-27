from functools import partial as _partial

from .base import Result, ReportCollection


def _comment_tone(review, df):

    return Result(
        df,
        x='labels.Code-Review.all_sets.comments',
        y='labels.Code-Review.all_sets.{0}'.format(review),
        kind='scatter'
    )


review_plus2 = _partial(_comment_tone, '+2',)
review_plus1 = _partial(_comment_tone, '+1',)
review_minus1 = _partial(_comment_tone, '-1',)
review_minus2 = _partial(_comment_tone, '-2',)


ReportCollection('comments').add_many({
    'review_plus2': review_plus2,
    'review_plus1': review_plus1,
    'review_minus1': review_minus1,
    'review_minus2': review_minus2,
})
