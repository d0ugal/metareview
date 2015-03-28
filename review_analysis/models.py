from elasticsearch_dsl import Search


class ReviewManager(object):

    def __init__(self, client):
        self.client = client

    def _all(self, search, limit=None):

        position = 0
        size = 100
        total = None

        while total is None or position < total:

            if limit is not None and position >= limit:
                break

            response = search[position:position+size].execute()

            total = response.hits.total
            position += size

            for hit in response:
                yield hit

    def all(self, limit=None, fields=None, filter_=None):

        s = Search(using=self.client, index="review")

        s.aggs.bucket('project_group', 'terms', field='project.group')
        s.aggs.bucket('project', 'terms', field='project')
        s.aggs.bucket('status', 'terms', field='status')

        if fields is not None:
            s = s.fields(fields)

        if filter_ is not None:
            s = s.filter("term", **filter_)

        for hit in self._all(s, limit):
            yield hit

    def aggr_count(self, col):

        s = Search(using=self.client, index="review")

        s.aggs.bucket(col, 'terms', field=col, size=1000)

        return getattr(s.execute().aggregations, col)['buckets']
