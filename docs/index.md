# Review Analysis

Review Analysis is a project for analysing code review data to
look find interesting data and create pretty graphs.

This project is under heavy development and currently rough
around the edges. Pull requests are more than welcome. At the
moment we only look at all the projects under the OpenStack
gerrit review data.

# Install

This currently requires a few steps at the moment.

    git clone https://github.com/d0ugal/review_analysis.git
    cd mkdocs;
    pip install -r requirements.txt
    python setup.py install

# Usage

## First time setup

First you will need some data to work with. At the moment we
currently only support the OpenStack deployment of Gerrit which
has over 140,000 reviews. You will need to create [an
account](https://review.openstack.org/#/) and take note of the
username and password under `HTTP Password` in the settings.

After you do this, you will need to follow these steps to fetch
the data.

    export GERRIT_USERNAME=$USERNAME
    export GERRIT_PASSWORD=$PASSWORD
    review_analaysis warm_cache

This will download around 5.3 Gb of JSON and store it under a
``_cache``. After this is finished (it will take a while) you are
set to examine the data. The cache doesn't invalidate and needs
to be manually busted by deleting the `_cache` directory.

## Viewing the data

After you have all the data, run the following command:

    review_analaysis report
    mkdocs serve

Then go to `localhost:8000` in your browser to see the data.
