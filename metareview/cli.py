from __future__ import print_function

import asyncio

import click

from metareview.gerrit import Gerrit
from metareview.graph import generate_all
from metareview.utils import cache_warmer


@click.group()
def cli():
    pass


@cli.command()
@click.option('--end', type=int)
def warm_cache(end):
    cache_warmer.start(end=end)


@cli.command()
@click.option('--end', type=int)
def graph_gen(end):
    gerrit = Gerrit(end=end)
    generate_all(gerrit)
