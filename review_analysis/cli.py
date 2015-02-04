from os import environ

import click

from review_analysis.reports import get_collections
from review_analysis.sources.gerrit import Gerrit
from review_analysis.util import dedent


@click.group()
def cli():
    pass


def common_options(f):
    """Applies a set of common click argument decorators to the
    function `f`.

    The arguments are --url, --username, --password, and --verbose.
    """
    return reduce(
        lambda f, d: d(f),
        (click.option('--url', type=str,
                      default='https://review.openstack.org'),
         click.option('--username', type=str,
                      default=environ.get('GERRIT_USERNAME')),
         click.option('--password', type=str,
                      default=environ.get('GERRIT_PASSWORD')),
         click.option('--verbose', is_flag=True, default=False)),
        f)


@cli.command()
@common_options
def warm_cache(url, username, password, verbose):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(
        password=password,
        url=url,
        username=username,
        verbose=verbose)
    for i, _ in enumerate(gerrit.reviews()):
        continue

    print "Warmed the cache for %s reviews" % i


@cli.command()
@common_options
@click.option('--limit', type=int)
@click.option('--collection', type=str, default=None)
@click.option('--cache-only', is_flag=True, default=True)
def report(url, username, password, verbose, limit, collection, cache_only):

    if cache_only:
        print 'Only using JSON already in the cache.'

    gerrit = Gerrit(
        cache_only=cache_only,
        password=password,
        url=url,
        username=username,
        verbose=verbose)

    for c in get_collections():

        if collection is not None and c.name != collection:
            continue

        df = gerrit.as_dataframe(limit, keys=c.required_keys)

        markdown = open('docs/reports/{0}.md'.format(c.slug), 'w')
        markdown.write('# {0}\n\n'.format(c.name))

        for name, report in c.reports.items():
            markdown.write('## {0}\n\n{1}\n\n'.format(
                name, dedent(getattr(report, '__doc__', ''))))
            try:
                print 'START: {0}:{1}'.format(c.name, report.slug), ' ... ',
                result = report(df)
                f = result.plot().get_figure()
                path = 'docs/images/{0}.{1}.png'.format(c.name, report.slug)
                f.savefig(path)
                markdown.write('![{0}]({1})\n\n'.format(path, path[4:]))
                print 'DONE'
            except Exception:
                print 'FAIL'
                raise

        markdown.close()
