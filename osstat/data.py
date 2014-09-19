from datetime import timedelta

import matplotlib as mpl
from pandas import DataFrame, to_datetime


def purty():
    from prettyplotlib.colors import set1 as ppl_colours
    context = mpl.rc_context(rc={
        'axes.color_cycle': ppl_colours,
        'lines.linewidth': .75
    })
    return context.__enter__()


def blah(reviews):

    for review in reviews:
        review = review.copy()

        delta = timedelta(minutes=review['owner.tz'])

        review['created'] = to_datetime(review['created'], errors='raise')

        if 'Workflow.approved.on' in review:
            review['Workflow.approved.on'] = to_datetime(
                review['Workflow.approved.on'])
            review['Workflow.approved.on.local'] = to_datetime(
                review['Workflow.approved.on']) + delta

        review['created.local'] = review['created'] + delta

        if 'merged.date' in review:
            review['merged.date'] = to_datetime(review['merged.date'])
            review['merged.date.local'] = review['merged.date'] + delta
            delta = review['merged.date'] - review['created']
            seconds = delta.total_seconds()

            if seconds > 0:
                review['review_duration'] = seconds

        yield review


def prepare_dataframe(client, cache_only=False):
    purty()
    return DataFrame.from_records(
        blah(client.reviews(cache_only)), index='created')
