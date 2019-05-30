"""
    Handlers for loading data from the VZ files.

    These files are typically provided by Mark Williams as Excel files
    
"""


import pandas as pd
import logging

from pylib.timeseries.timeseries import TimeSeries

YEAR_COL = 'Time'

SKIP_ROWS = [2]

def read_file(filename):
    with open(filename, 'r') as f:
        logging.info("reading input file: '{}'".format(filename))
        return pd.read_csv(filename, header=1, skiprows=SKIP_ROWS)


class GWData:
    """
        Represents Raw Data from solid waste release

    """
    def __init__(self, filename):
        self.df = read_file(filename)
    
    @property
    def get_rowcols(self):
        columns = self.df.columns[1:]
        return columns

    def extract(self, row, col):
        """ extract [times], [values] for the row/col """
        column_label = '-'.join([row, col])
        sub = self.df[column_label].values
        x = self.df[YEAR_COL].values
        y = sub
        return TimeSeries(x, y, row, col)
