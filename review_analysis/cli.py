from itertools import islice
from os import environ

import click
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from review_analysis.sources.gerrit import Gerrit
from review_analysis.util import dedent, grouper


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
@click.option('--limit', type=int)
def warm_cache(url, username, password, verbose, limit):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(
        password=password,
        url=url,
        username=username,
        verbose=verbose)
    for i, _ in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break
        continue

    print "Warmed the cache for %s reviews" % i


@cli.command()
@common_options
@click.argument('ip', type=str)
@click.option('--limit', type=int)
def es_bulk_load(url, username, password, verbose, limit, ip, reset=True):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(
        cache_only=True,
        password=password,
        url=url,
        username=username,
        verbose=verbose)

    reviews_gen = islice(gerrit.reviews_es_bulk_format(), limit)

    es = Elasticsearch(ip)

    if reset and es.indices.exists('review'):
        print "Resetting."
        es.indices.delete('review')
        es.indices.create('review')
        print "Reset dome."

    bulk_size = 500

    print "Starting load"

    for i, review_group in enumerate(grouper(bulk_size, reviews_gen), start=1):
        count, errors = bulk(es, review_group)

        if count != bulk_size or len(errors):
            print count, errors
            raise Exception("uh oh")

        print "Loaded {}".format(i * bulk_size)

    print "Load finished, optimizing"
    es.indices.optimize('review')
    print "Optimize finished"


@cli.command()
@common_options
@click.option('--limit', type=int)
@click.option('--collection', type=str, default=None)
@click.option('--cache-only', is_flag=True, default=False)
def report(url, username, password, verbose, limit, collection, cache_only):

    if cache_only:
        print 'Only using JSON already in the cache.'

    gerrit = Gerrit(
        cache_only=cache_only,
        password=password,
        url=url,
        username=username,
        verbose=verbose)

    from review_analysis.reports import get_collections
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
