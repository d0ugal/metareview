from __future__ import print_function

import asyncio

import click

from metareview.gerrit import Gerrit, guess_total_reviews
from metareview.graph import generate_all
from metareview.utils import cache_warmer


_COUNT = guess_total_reviews()


@click.group()
def cli():
    pass


@cli.command()
@click.option('--end', type=int, default=_COUNT)
def warm_cache(end):
    print("Fetching until", end)
    cache_warmer.start(end=end)


@cli.command()
@click.option('--end', type=int, default=_COUNT)
def graph_gen(end):
    print("Fetching until", end)
    gerrit = Gerrit(end=end)
    generate_all(gerrit)
