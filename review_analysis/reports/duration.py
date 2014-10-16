from functools import partial as _partial

import numpy as _np

from .base import Result


def _duration(groupby, at_least, df):
    df = df[df['status'] == 'MERGED']
    df['review_duration.hours'] = df['review_duration'] / 60 / 60
    by_developer = df.groupby(groupby)
    speed = by_developer['review_duration.hours'].aggregate([
        _np.mean, _np.std, len])
    speed = speed[speed['len'] > at_least]
    speed.sort('mean', ascending=True, inplace=True)
    return Result(speed)


developer = _partial(_duration, ['owner._account_id'], 10)
project = _partial(_duration, ['project'], 100)
project_group = _partial(_duration, ['project.group'], 0)
submitted_hour = _partial(_duration, ['created.hour'], 0)
submitted_hour_local = _partial(_duration, ['created.local.hour'], 0)
