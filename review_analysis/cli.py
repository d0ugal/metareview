from os import environ

import click

from review_analysis.sources.gerrit import Gerrit
from review_analysis.stores import db


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

    for i, _ in enumerate(gerrit.reviews()):
        if i == limit:
            break
        continue

    print "Warmed the cache for %s reviews" % i


@cli.command()
def initdb():
    db.initdb()


@cli.command()
@common_options
@click.option('--limit', type=int)
def loaddb(url, username, password, verbose, limit):
    gerrit = Gerrit(
        password=password,
        url=url,
        username=username,
        verbose=verbose)

    session = db.Session()

    ids = set()

    for i, change in enumerate(gerrit.reviews()):
        if i == limit:
            break

        if i % 1000 == 0:
            print "Loaded {} reviews. {}".format(i, len(ids))

        change_id = change['_number']
        ids.add(change_id)

        try:
            q = session.query(db.Change).filter(db.Change.id == change_id)

            if not bool(q.count()):
                session.add(db.Change(id=change['_number'], data=change))
                session.commit()
            else:
                print change_id

        except:
            print change_id
            raise

    print "Warmed the cache for %s reviews" % i
