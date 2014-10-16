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
