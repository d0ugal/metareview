from datetime import timedelta

from pandas import DataFrame, to_datetime


def blah(reviews):
    for review in reviews:
        review = review.copy()

        review['created'] = to_datetime(review['created'])

        if 'Workflow.approved.on' in review:
            review['Workflow.approved.on'] = to_datetime(
                review['Workflow.approved.on'])

        delta = timedelta(minutes=review['owner.tz'])
        review['created_local'] = review['created'] + delta

        if 'merged.date' in review:
            review['merged.date'] = to_datetime(review['merged.date'])
            review['review_duration'] = (
                review['merged.date'] - review['created']).seconds

        yield review


def prepare_dataframe(client, cache_only=False):
    return DataFrame.from_records(
        blah(client.reviews(cache_only)), index='created')
