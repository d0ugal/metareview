from functools import partial

from .base import Result, ReportCollection


def _comment_tone(review, df):
    """
    Compare the number of comments in a review versus the review
    outcome. As a review get more comments, is the outcome more
    likely to be positive or negative?
    """

    return Result(
        df,
        x='labels.Code-Review.all_sets.comments',
        y='labels.Code-Review.all_sets.{0}'.format(review),
        kind='scatter'
    )


review_plus2 = partial(_comment_tone, '+2',)
review_plus1 = partial(_comment_tone, '+1',)
review_minus1 = partial(_comment_tone, '-1',)
review_minus2 = partial(_comment_tone, '-2',)


ReportCollection('Comments', [
    '_number',
    'labels.Code-Review.all_sets.comments',
    'labels.Code-Review.all_sets.+2',
    'labels.Code-Review.all_sets.+1',
    'labels.Code-Review.all_sets.-1',
    'labels.Code-Review.all_sets.-2',
]).add_many((
    ("No. comments vs the no. +2's", review_plus2),
    ("No. comments vs the no. +1's", review_plus1),
    ("No. comments vs the no. -1's", review_minus1),
    ("No. comments vs the no. -2's", review_minus2),
))
