from functools import partial as _partial
import numpy as _np

from .base import Result, ReportCollection


def rating(df, minimum_reviews=25):
    """
    Given the data frame, group by owner._account_id and
    aggregate the number the reviews they have received. Sort
    the results to show reviewers with the most overall reviews.
    """

    by_developer = df.groupby(['owner._account_id'])

    rating = by_developer[[
        'labels.Code-Review.all_sets.all',
        'labels.Code-Review.all_sets.-2',
        'labels.Code-Review.all_sets.-1',
        'labels.Code-Review.all_sets.+1',
        'labels.Code-Review.all_sets.+2',
    ]].aggregate([_np.sum, len])

    multi_index = ('labels.Code-Review.all_sets.all', 'len')
    rating = rating[rating[multi_index] > minimum_reviews]

    rating['% +ve'] = (
        (
            rating['labels.Code-Review.all_sets.+2']['sum'] +
            rating['labels.Code-Review.all_sets.+1']['sum']
        ) / (rating['labels.Code-Review.all_sets.all']['sum'] * 1.0)
    ) * 100.0

    rating = rating[[
        '% +ve',
        'labels.Code-Review.all_sets.all',
        'labels.Code-Review.all_sets.+1',
        'labels.Code-Review.all_sets.+2',
    ]].sort(['% +ve'], ascending=False)

    return Result(
        rating
    )


def number_of_timezones(df):
    """
    Find the developers with reviews submitted from the most
    different timezones.
    """
    by_developer = df.groupby(['owner._account_id'])
    tz_count = by_developer['owner.tz'].aggregate(lambda x: len(set(x)))
    tz_count.sort('owner.tz', ascending=False, inplace=True)

    return Result(
        tz_count.to_frame(),
        plot=_partial(tz_count.head().plot, kind='bar')
    )

ReportCollection('developer', [
    'owner._account_id',
    'owner.tz',
    'labels.Code-Review.all_sets.all',
    'labels.Code-Review.all_sets.-2',
    'labels.Code-Review.all_sets.-1',
    'labels.Code-Review.all_sets.+1',
    'labels.Code-Review.all_sets.+2',
]).add_many((
    ('rating', rating),
    ('number_of_timezones', number_of_timezones)
))
