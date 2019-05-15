""" represents a timeseries """
import scipy.signal as signal
from scipy.integrate import cumtrapz as cumtrapz, trapz
import numpy as np
from pylib.vzreducer.config import config
import pylib.vzreducer.constants as c


class TimeSeries:
    """ Represents a particular site/copc's timeseries 
    
        times is array-like
        values is array-like (indexted the same as times)
        copc is a string
        site is a string
    
    """
    def __init__(self, times, values, copc, site):
        self.site = site
        self.copc = copc
        self.times = times
        self.values = values

    @classmethod
    def from_values(cls, timeseries, values):
        """
            Create a new TimeSeries by replacing the values;
            everything else is the same

        """
        return cls(times=timeseries.times, values=values,
                copc=timeseries.copc,
                site=timeseries.site)

    def __eq__(self, timeseries):
        """ timeseries are equivalent if times and values are equal"""
        times = self.times==timeseries.times
        values = self.values==timeseries.values
        return np.all(times) and np.all(values)

    def __len__(self):
        return len(self.times)

    def are_all_zero(self):
        """ true if everything is zero """
        return np.all(self.values==0)

    def get_peaks(self):
        """ find the location of the peaks"""
        peaks, _ = signal.find_peaks(self.values)
        peaks_neg, _ = signal.find_peaks(-self.values)
        peaks = np.concatenate((self.times[peaks], self.times[peaks_neg]))
        return np.concatenate((peaks, peaks_neg))
            

    def subset(self, timesteps):
        """ return a TimeSeries with the specific timesteps """
        times = self.times
        values = self.values
        condition = [i in timesteps for i in self.times]
        out = values[condition]
        return TimeSeries(times[condition], out, self.copc, self.site)

