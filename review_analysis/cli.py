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
@click.option('--start', type=int, default=1)
@click.option('--end', type=int)
def warm_cache(url, username, password, verbose, end, start, limit):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(password=password, url=url, username=username,
                    verbose=verbose, start=start, end=end)

    for i, _ in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break
        continue
    else:
        print "No reviews? start={}, end={}, limit={}".format(start, end, limit)
        return

    print "Warmed the cache for %s reviews" % i


@cli.command()
@common_options
@click.option('--limit', type=int)
@click.option('--author', type=str)
@click.option('--owner', type=str)
@click.argument('output', type=click.File('wb'))
def extract_comments(url, username, password, verbose, output, owner, author,
                     limit):

    gerrit = Gerrit(password=password, url=url, username=username,
                    verbose=verbose, cache_only=True)

    for i, review in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break

        if i % 1000 == 0:
            print i

        if owner and review.get('owner', {}).get('username') != owner:
            continue

        for comment in review['messages']:

            if author and comment.get('author', {}).get('username') != author:
                continue

            c = comment['message'].encode('utf-8')
            c = c.replace("Patch Set", "")
            c = c.replace("Looks good to me, but someone else must approve", "")
            c = c.replace("Uploaded patch set", "")
            c = c.replace("I would prefer that you didn't merge this", "")
            c = c.replace("Ready For Review", "")
            c = c.replace("Code-Review", "")
            c = c.replace(" inline comment)", "")
            c = c.replace(" inline comments)", "")
            c = c.replace(" comment)", "")
            c = c.replace(" comments)", "")
            c = c.replace(": Work In Progress", "")
            c = c.replace("Workflow-1", "")
            c = c.replace("was rebased", "")
            c = c.replace("Commit message was updated", "")
            c = c.replace("Automatically re-added by Gerrit trivial rebase detection script", "")

            output.write(c)
            output.write("\n")

    print "Extracted comments for {} reviews".format(i)
