class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)

import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 200)

from review_analysis.sources.gerrit import Gerrit
from review_analysis import reports

__all__ = ('pd', 'np', 'reports', 'Gerrit')

print "Finished setup"
