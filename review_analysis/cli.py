import click

from review_analysis.sources.gerrit import create_gerrit_connection


@click.group()
def cli():
    pass


@cli.command()
@click.option('--url', type=str, default='https://review.openstack.org')
@click.option('--username', type=str, default=None)
@click.option('--password', type=str, default=None)
@click.option('--verbose', is_flag=True, default=False)
def warm_cache(url, username, password, verbose):
    """
    Download all of the datas.
    """
    gerrit = create_gerrit_connection(
        url=url,
        username=username,
        password=password,
        verbose=verbose)
    for i, _ in enumerate(gerrit.reviews()):
        continue

    print "Warmed the cache for %s reviews" % i


@cli.command()
@click.option('--limit', type=int)
@click.option('--url', type=str, default='https://review.openstack.org')
@click.option('--username', type=str, default=None)
@click.option('--password', type=str, default=None)
@click.option('--verbose', is_flag=True, default=False)
def report(limit, url, username, password, verbose):
    gerrit = create_gerrit_connection(
        username=username,
        password=password,
        url=url,
        verbose=verbose)

    df = gerrit.as_dataframe(limit)

    print df
