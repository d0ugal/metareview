from .base import Result


def size_vs_reviews(df, line_count='lines_diff'):
    df = df[df['revisions.totals.{0}'.format(line_count)] < 5000]
    df = df[df['revisions.totals.{0}'.format(line_count)] > -5000]

    return Result(
        df,
        x='revisions.totals.{0}'.format(line_count),
        y='labels.Code-Review.all_sets.all',
        kind='scatter'
    )
