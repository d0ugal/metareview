from __future__ import print_function

import click

from metareview.gerrit import Gerrit


@click.group()
def cli():
    pass


@cli.command()
@click.option('--verbose', is_flag=True, default=False)
@click.option('--limit', type=int)
@click.option('--start', type=int, default=1)
@click.option('--end', type=int)
def warm_cache(verbose, end, start, limit):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(verbose=verbose, start=start, end=end)

    for i, _ in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break
        continue
    else:
        print("No reviews? start={},end={},limit={}".format(start, end, limit))
        return

    print ("Warmed the cache for %s reviews" % i)
