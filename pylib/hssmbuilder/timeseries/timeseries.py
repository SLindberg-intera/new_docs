""" represents a timeseries """
import scipy.signal as signal
from scipy.integrate import cumtrapz as cumtrapz, trapz
import numpy as np
import pylib.timeseries.timeseries_math as ts_math


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

    def __sub__(self, b):
        """
            facilitates subtraction: a - b 


            if the TimeSeries are not time-aligned, it will
            first interpolate the "b" timeseries at "a"'s timesteps.

        """
        return ts_math.delta(self, b)

    def from_values(self, values):
        """
            Create a new TimeSeries by replacing the values;
            everything else is the same

        """
        if len(values)!=len(self):
            raise ValueError("Values did not have same length as TimeSeries")

        return TimeSeries(times=self.times, values=values,
                copc=self.copc,
                site=self.site)

    def interpolate_at_timeseries(self, timeseries):
        """ interpolates self at the values from timeseries """
        return ts_math.interpolated(self, timeseries)

    def __eq__(self, timeseries):
        """ timeseries are equivalent if times and values are equal"""
        times = self.times==timeseries.times
        values = self.values==timeseries.values
        return np.all(times) and np.all(values)

    def __len__(self):
        return len(self.times)

    def integrate(self):
        return ts_math.integrate(self)

    def are_all_zero(self):
        """ true if everything is zero """
        return np.all(self.values==0)

    def get_peaks(self):
        """ find the location of the peaks"""
        peaks, _ = signal.find_peaks(self.values)
        peaks_neg, _ = signal.find_peaks(-self.values)
        peaks = np.concatenate((self.times[peaks], self.times[peaks_neg]))
        return np.concatenate((peaks, peaks_neg))

    def slice(self, from_ix, upto_ix):
        """ equivalent to the numpy A[from:to] operation for an array A"""
        x = self.times[from_ix:upto_ix]
        y = self.values[from_ix:upto_ix]
        return TimeSeries(times=x, values=y, copc=self.copc, site=self.site)

    def subset(self, timesteps):
        """ return a TimeSeries with the specific timesteps """
        times = self.times
        values = self.values
        condition = [i in timesteps for i in self.times]
        out = values[condition]
        return TimeSeries(times[condition], out, self.copc, self.site)

