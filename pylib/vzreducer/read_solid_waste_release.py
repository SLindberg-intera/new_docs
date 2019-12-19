"""
    Handlers for loading data from the Solid Waste Release files.

    These files are typically provided by Ryan Nell as Excel files
    where there is one file for 200W and one for 200E

"""


import pandas as pd
import logging

from pylib.timeseries.timeseries import TimeSeries

SITE_COL = 'Site_Name'
YEAR_COL = 'Year'

SKIP_ROW = 1

def read_solid_waste_file(filename):
    with open(filename, 'r') as f:
        logging.info("reading input file: '{}'".format(filename))
        return pd.read_csv(filename, header=0, skiprows=[SKIP_ROW,])


class SolidWasteReleaseData:
    """
        Represents Raw Data from solid waste release

    """
    def __init__(self, filename, zero_below=''):
        self.df = read_solid_waste_file(filename)
        self.zero_below = zero_below
        if zero_below == '':
            self.zero_below = None
            logging.info("NOTE: No flux values are reset to 0")
        #SLL--converted zero_below from string to a float to avoid type error
        else:
            self.zero_below = float(zero_below)
            logging.info("NOTE: Fluxes less than the user-defined value of {} are set to 0 [zero]".format(str(self.zero_below)))
        logging.info("COPCS in {}: {}".format(filename, str(self.copcs)))
        logging.info("Sites in {}: {}".format(filename, str(self.sites)))

    @property
    def copcs(self):
        """ return a list of the unique copcs in the file """
        try:
            return self._copcs
        except AttributeError:
            self._copcs = list(set(self.df.columns) - {YEAR_COL, SITE_COL})
        return self.copcs

    @property
    def sites(self):
        """ return a list of the unique waste site ids in the file"""
        try:
            return self._sites
        except AttributeError:
            self._sites = list(set(self.df[SITE_COL].values))
        return self.sites    

    def extract(self, copc, site):
        """ extract [times], [values] for the copc/site """
        sub = self.df[self.df[SITE_COL]==site]
        x = sub[YEAR_COL].values
        y = sub[copc].values
        if self.zero_below is not None:
            idx = y < self.zero_below

        if self.zero_below is not None and any(idx):
            #idx = y < self.zero_below

            msg = "{}--{}: Forcing values less than '{}' to zero; occurs at \ntimesteps: {} \nwith corresponding flux: {} "
            logging.info(msg.format(
                site, copc, self.zero_below,
                x[idx], y[idx]
                                    )
                       )
            y[idx] = 0.0

        return TimeSeries(x, y, copc, site)
