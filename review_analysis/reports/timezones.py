from .base import Result, ReportCollection


def spread(df):
    df['owner.tz.hour'] = df['owner.tz'] / 60.0
    counts_by_hour = df.groupby('owner.tz.hour')

    return Result(
        counts_by_hour['owner._account_id'].count(),
        kind='bar'
    )

ReportCollection('timezones', [
    'owner.tz',
    'owner._account_id',
]).add('spread', spread)
