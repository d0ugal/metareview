class Result(object):

    def __init__(self, df, plot=None, **plot_args):

        self.data = df
        self._plot = plot
        self._plot_args = plot_args

    def plot(self, **plot_args):

        if not plot_args and self._plot:
            return self._plot()

        args = self._plot_args.copy()
        args.update(plot_args)

        return self.data.plot(**args)

_collections = []


class ReportCollection(object):

    def __init__(self, name):
        self.name = name
        self.reports = {}
        _collections.append(self)

    def add(self, name, reporter):

        if self.name in self.reports:
            raise ValueError("Name '{0}' already in use.".format(name))

        self.reports[name] = reporter

    def add_many(self, reporters):
        for name, reporter in reporters.items():
            self.add(name, reporter)


def get_collections():
    return _collections
