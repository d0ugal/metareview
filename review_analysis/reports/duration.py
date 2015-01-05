from functools import partial as _partial

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


developer = _partial(_duration, ['owner._account_id'])
project = _partial(_duration, ['project'])
project_group = _partial(_duration, ['project.group'])
submitted_hour = _partial(_duration, ['created.hour'], top=False)
submitted_hour_local = _partial(_duration, ['created.local.hour'], top=False)

ReportCollection('duration', [
    'status',
    'review_duration',
    'owner._account_id',
    'project',
    'project.group',
    'created.hour',
    'created.local.hour',
]).add_many((
    ('developer', developer),
    ('project', project),
    ('project_group', project_group),
    ('submitted_hour', submitted_hour),
    ('submitted_hour_local', submitted_hour_local),
))
