from os import environ

import click

from review_analysis.gerrit import Gerrit


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
    gerrit = Gerrit(password=password, url=url, username=username,
                    verbose=verbose)

    for i, _ in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break
        continue

    print "Warmed the cache for %s reviews" % i


@cli.command()
@common_options
@click.option('--limit', type=int)
@click.option('--author', type=str)
@click.argument('output', type=click.File('wb'))
def extract_comments(url, username, password, verbose, output, author, limit):

    gerrit = Gerrit(password=password, url=url, username=username,
                    verbose=verbose, cache_only=True)

    for i, review in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break

        for comment in review['messages']:

            if author and comment.get('author', {}).get('username') != author:
                continue

            output.write(comment['message'].encode('utf-8'))
            output.write("\n")

    print "Extracted comments for {} reviews".format(i)
