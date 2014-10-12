import numpy as np


def number_of_reviews(df):
    """
    Given a data frame, group by the number of reviewers that
    have reviewed this patch and return the grouped count.
    """
    by_reviews = df.groupby(['labels.Code-Review.totals.all'])
    return by_reviews['created'].count()


def developer_rating(df):
    """
    Given the data frame, group by owner._account_id and
    aggregate the number the reviews they have received. Sort
    the results to show reviewers with the most overall reviews.
    """

    by_developer = df.groupby(['owner._account_id'])

    rating = by_developer[[
        'labels.Code-Review.totals.all',
        'labels.Code-Review.totals.-2',
        'labels.Code-Review.totals.-1',
        'labels.Code-Review.totals.0',
        'labels.Code-Review.totals.+1',
        'labels.Code-Review.totals.+2',
    ]].aggregate([np.mean, np.sum, len, min, max])

    nested_sort = [("labels.Code-Review.totals.all", 'len')]

    rating.sort(nested_sort, ascending=False)

    rating['% +ve'] = (
        rating['labels.Code-Review.totals.+2']['sum']
        / rating['labels.Code-Review.totals.all']['sum'])
    rating = rating[[
        '% +ve',
        'labels.Code-Review.totals.all',
        'labels.Code-Review.totals.+2',
    ]].sort(['% +ve'], ascending=False)

    return rating


def developer_timezone(df):
    """
    Find the developers with reviews submitted from the most
    different timezones.
    """
    by_developer = df.groupby(['owner._account_id'])
    tz_count = by_developer['owner.tz'].aggregate(lambda x: len(set(x)))
    tz_count.sort('owner.tz', ascending=False)
    return tz_count.to_frame()


def developer_speed(df):
    by_developer = df.groupby(['owner._account_id'])
    speed = by_developer['review_duration'].aggregate([np.mean, np.std])
    return speed


def timezones(df):
    df['owner.tz.hour'] = df['owner.tz'] / 60.0
    counts_by_hour = df.groupby('owner.tz.hour')
    counts_by_hour['owner._account_id'].count().plot(kind='bar')


__all__ = [
    'number_of_reviews',
    'developer_rating',
    'developer_timezone',
    'developer_speed'
]
