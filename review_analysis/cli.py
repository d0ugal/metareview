from os import environ

import os
import click
from simplejson import dumps

from review_analysis.sources.gerrit import Gerrit
from review_analysis.util import dedent, encode_conplex


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
@click.argument('output', type=click.Path(file_okay=False, exists=True))
@click.argument('ip', type=str)
@click.option('--limit', type=int)
def es_bulk_load(url, username, password, verbose, limit, output, ip):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(
        cache_only=True,
        password=password,
        url=url,
        username=username,
        verbose=verbose)

    reviews = gerrit.reviews()

    outf = None

    print """#!/bin/bash

set -e;
set -x;
"""

    print "curl -XDELETE 'http://{0}:9200/_all';".format(ip)
    print "curl -XDELETE 'http://{0}:9200/_all';".format(ip)
    print "curl -XDELETE 'http://{0}:9200/review/_mapping';".format(ip)

    batch_size = 1000

    for i, review in enumerate(reviews):

        if outf is None or i % batch_size == 0:
            if outf is not None:
                outf.close()
            path = os.path.join(output, 'file-{}.json'.format(i/batch_size))
            outf = open(path, 'wa')
            print "curl -s -XPOST {0}:9200/_bulk --data-binary @{1};".format(
                ip, outf.name)

        if i == limit:
            break

        outf.write(dumps({
            "index": {
                "_index": "review",
                "_type": "review-openstack-org",
                "_id": review['id'],
            }
        }))
        outf.write("\n")
        outf.write(dumps(review, default=encode_conplex))
        outf.write("\n")

    print "curl -XPOST 'http://{0}:9200/review/_optimize';".format(ip)
    print ("echo 'Output %s reviews in Elasticsearch bulk "
           "format';" % (i + 1))


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
