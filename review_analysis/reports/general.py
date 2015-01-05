from .base import Result, ReportCollection


def number_of_reviews(df):
    """
    Given a data frame, group by the number of reviewers that
    have reviewed this patch and return the grouped count.
    """
    by_reviews = df.groupby('labels.Code-Review.totals.all')

    return Result(
        by_reviews['created'].count(),
        kind='bar'
    )

ReportCollection('general', [
    'created',
    'labels.Code-Review.totals.all',
]).add_many((
    ('number_of_reviews', number_of_reviews),
))
