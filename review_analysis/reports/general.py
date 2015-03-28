from pandas import DataFrame

from .base import ReportCollection


def number_of_reviews(review_manager):

    result = review_manager.aggr_count("labels.Code-Review.totals.all")
    df = DataFrame(result).set_index('key').sort_index()
    df.columns = ["Review Count", ]

    plot = df.plot(kind="bar", figsize=(12, 8))

    plot.set_xlabel("Number of times reviewed")
    plot.set_ylabel("Number of reviews")


ReportCollection('general').add_many((
    ('Number of reviews per patch', number_of_reviews),
))
