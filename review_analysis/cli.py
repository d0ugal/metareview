import click

from review_analysis.sources.gerrit import Gerrit


@click.group()
def cli():
    pass


@cli.command()
@click.option('--url', type=str)
def warm_cache(url):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(verbose=True, url=url)
    for i, _ in enumerate(gerrit.reviews()):
        continue

    print "Warmed the cache for %s reviews" % i


@cli.command()
@click.option('--limit', type=int)
def report(limit):
    gerrit = Gerrit()

    df = gerrit.as_dataframe(limit)

    print df
