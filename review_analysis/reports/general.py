from .base import Result


def number_of_reviews(df):
    """
    Given a data frame, group by the number of reviewers that
    have reviewed this patch and return the grouped count.
    """
    by_reviews = df.groupby(['labels.Code-Review.totals.all'])

    return Result(
        by_reviews['created'].count(),
        kind='bar'
    )
