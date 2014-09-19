import click

from osstat.client import StatClient
from osstat.data import prepare_dataframe


@click.command()
@click.option('--cache-only/--no-cache', default=False)
def hello(cache_only):

    if cache_only:
        print "only using the cached files."

    client = StatClient()
    df = prepare_dataframe(client, cache_only=cache_only)

    df.sort_index(axis=1)
    df.to_csv('openstack-data.csv', encoding='utf-8')

if __name__ == '__main__':
    hello()
