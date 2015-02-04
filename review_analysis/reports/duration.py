from functools import partial

import numpy as _np

from .base import Result, ReportCollection


def _duration(groupby, df, top=True):
    df = df[df['status'] == 'MERGED']
    df['review_duration.hours'] = df['review_duration'] / 60 / 60
    by_developer = df.groupby(groupby)
    speed = by_developer['review_duration.hours'].aggregate([
        _np.mean, _np.std])
    speed = speed.sort('mean', ascending=True, inplace=False)
    if top:
        speed = speed[:10]
    else:
        speed = speed[:-10]
    return Result(speed, kind='bar')


developer = partial(_duration, ['owner._account_id'])
project = partial(_duration, ['project'])
project_group = partial(_duration, ['project.group'])
submitted_hour = partial(_duration, ['created.hour'], top=False)
submitted_hour = partial(_duration, ['created.hour'])

ReportCollection('Duration', [
    'status',
    'review_duration',
    'owner._account_id',
    'project',
    'project.group',
    'created.hour',
    'created.local.hour',
]).add_many((
    ('The fastest developer', developer),
    ('The fastest project', project),
    ('The fastest Project Group', project_group),
    ('The fastest hour (UTC)', submitted_hour),
))
