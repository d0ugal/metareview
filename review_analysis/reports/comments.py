import seaborn as sns
from pandas import DataFrame


from .base import ReportCollection


def comment_tone(review_manager):
    """
    Compare the number of comments in a review versus the review
    outcome. As a review get more comments, is the outcome more
    likely to be positive or negative?
    """

    fields = [
        'labels.Code-Review.all_sets.comments',
        'labels.Code-Review.all_sets.+1',
        'labels.Code-Review.all_sets.-1',
        'labels.Code-Review.all_sets.-2',
        'labels.Code-Review.all_sets.+2',
    ]

    sns.set(style="ticks", context="talk")

    results = review_manager.all(fields=fields, filter_={
        'status': 'ABANDONDED',
        'project.group': 'openstack'
    })

    data = []

    for result in results:
        for field in fields[1:]:
            if result.get(field, [0, ])[0] == 0:
                continue
            data.append([
                result[fields[0]][0],
                result.get(field, [0, ])[0],
                field[-2:]
            ])

    df = DataFrame.from_records(data)
    df.columns = ["comments", "scores", "score"]

    print len(df)

    hue_order = ["+2", "+1", "-1", "-2"]
    sns.lmplot("scores", "comments", hue="score", data=df, hue_order=hue_order,
               figsize=(12, 8))

ReportCollection('Comments').add_many((
    ("Number of comments vs review scores", comment_tone),
))
