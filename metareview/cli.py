from __future__ import print_function

import click

from metareview.gerrit import Gerrit


@click.group()
def cli():
    pass


@cli.command()
@click.option('--verbose', is_flag=True, default=False)
@click.option('--limit', type=int)
@click.option('--start', type=int, default=1)
@click.option('--end', type=int)
def warm_cache(verbose, end, start, limit):
    """
    Download all of the datas.
    """
    gerrit = Gerrit(verbose=verbose, start=start, end=end)

    for i, _ in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break
        continue
    else:
        print("No reviews? start={},end={},limit={}".format(start, end, limit))
        return

    print ("Warmed the cache for %s reviews" % i)


@cli.command()
@click.option('--verbose', is_flag=True, default=False)
@click.option('--limit', type=int)
@click.option('--author', type=str)
@click.option('--owner', type=str)
@click.argument('output', type=click.File('wb'))
def extract_comments(verbose, output, owner, author, limit):

    gerrit = Gerrit(verbose=verbose, cache_only=True)

    for i, review in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break

        if i % 1000 == 0:
            print(i)

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
            c = c.replace("Automatically re-added by Gerrit trivial rebase "
                          "detection script", "")

            output.write(c)
            output.write("\n")

    print("Extracted comments for {} reviews".format(i))


@cli.command()
@click.option('--verbose', is_flag=True, default=False)
@click.option('--limit', type=int)
@click.option('--author', type=str)
@click.option('--owner', type=str)
@click.argument('output', type=click.File('wb'))
def extract_subject(verbose, output, owner, author, limit):

    gerrit = Gerrit(verbose=verbose, cache_only=True)

    for i, review in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break

        try:
            sha = review['current_revision']
        except:
            print(review['_number'])
            continue
        s = review['revisions'][sha]['commit']['subject'].encode('utf-8')
        output.write(s)
        output.write("\n")

    print("Extracted subjects for {} reviews".format(i))


@cli.command()
@click.option('--verbose', is_flag=True, default=False)
@click.option('--limit', type=int)
@click.option('--author', type=str)
@click.option('--owner', type=str)
@click.argument('output', type=click.File('wb'))
def extract_commit_msg(verbose, output, owner, author,
                       limit):

    gerrit = Gerrit(verbose=verbose, cache_only=True)

    for i, review in enumerate(gerrit.reviews(), start=1):
        if i == limit:
            break

        try:
            sha = review['current_revision']
        except:
            print(review['_number'])
            continue
        s = review['revisions'][sha]['commit']['message'].encode('utf-8')

        output.write(s)
        output.write("\n")

    print("Extracted subjects for {} reviews".format(i))
