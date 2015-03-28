from itertools import islice
from os import environ

import click
import time
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import matplotlib.pyplot as plt

from review_analysis.models import ReviewManager
from review_analysis.sources.gerrit import Gerrit
from review_analysis.reports import get_collections
from review_analysis.util import grouper, ensure_directory


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
@click.option('--skip', type=int)
@click.option('--reset', is_flag=True)
def es_load(url, username, password, verbose, limit, ip, skip=0, reset=False):
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
        print "Reset done."

    bulk_size = 500

    print "Starting load"

    for i, review_group in enumerate(grouper(bulk_size, reviews_gen), start=1):

        progress = i * bulk_size

        if progress <= skip:
            print "Skipped {}".format(progress)
            continue

        for i in range(5):
            try:
                count, errors = bulk(es, review_group)
                break
            except Exception as e:
                print "Retrying due to {0} ({1}/5)".format(e, i)

        if count != bulk_size or len(errors):
            print count, errors
            raise Exception("uh oh")

        print "Loaded {}".format(progress)

    print "Load finished, optimizing"
    es.indices.optimize('review')
    print "Optimize finished"


@cli.command()
@click.argument('ip', type=str)
@click.option('--limit', type=int)
@click.option('--collection', type=str)
@click.option('--debug', is_flag=True)
def report(limit, ip, collection, debug=False):

    es = Elasticsearch(ip)
    reviews = ReviewManager(es)

    for c in get_collections():

        if collection is not None and c.slug != collection:
            continue

        print "\nCOLLECTION: {0}".format(c.slug)

        for name, report in c.reports.items():

            print "\tREPORT: {0}".format(report.slug)
            start = time.time()
            try:
                plt.figure()
                report(reviews)
                ensure_directory("images/{0}/".format(c.slug))
                path = "docs/images/{0}/{0}.png".format(c.slug, report.slug)
                plt.savefig(path, format="png")
                print "\t\tDONE ({0}s)".format(time.time() - start)
            except Exception as e:
                if debug:
                    raise
                print "\t\tFAIL ({0:.2f}s)".format(time.time() - start), str(e)
