""" represents a timeseries """
import scipy.signal as signal
from scipy.integrate import cumtrapz as cumtrapz
import numpy as np
from pylib.vzreducer.config import config
import pylib.vzreducer.constants as c

def smooth(timeseries):
    """ smooth the data set """
    x = timeseries.times
    y = timeseries.values
    
    N = config[c.SMOOTH_KEY][c.BUTTER_INDEX_KEY]
    f_c = config[c.SMOOTH_KEY][c.CUTOFF_FREQUENCY]
    B, A = signal.butter(N, f_c, output='ba')
    smoothed = signal.filtfilt(B, A, y)

    return smoothed


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

    def smooth(self):
        """ return a new instanced with smoothed data """ 
        smoothed_values = smooth(self)
        return TimeSeries(self.times, smoothed_values, 
                self.copc, self.site)

    def get_residual(self):
        """ Return an instance of Residual from self """
        return Residual(self)

    def integrate(self):
        """ integrate as a cumulative trap"""
        y_int = cumtrapz(self.values, self.times, initial=0)
        return TimeSeries(self.times, y_int, self.copc, self.site)

class Residual:
    """  Represents a signal with an estimate
            of its error
    """
    def __init__(self, timeseries):
        self.raw = timeseries
        self.smoothed = timeseries.smooth()
        self.errors = self.estimate_error_series()
        self.error_mean = np.mean(np.abs(self.errors.values))/(
                np.sqrt(len(self.errors.times))
                )
        
        self.error_std = np.std(np.abs(self.errors.values))
        self.mass_error = self._mass_error()

    def _mass_error(self):
        """ effectively integrating the error in the flux
        to get an estimate of the accumlative error in the mass
        
        """
        return self.error_mean*(len(self.raw.times))

    def estimate_error_series(self):
        """
            estimate the error by subtracting the
            smoothed signal from the raw signal
        """
        v = self.raw.values - self.smoothed.values
        copc = self.raw.copc
        site = self.raw.site
        return TimeSeries(self.raw.times,  v, copc, site)

    def region_large_error(self):
        """ return a TimeSeries that only has the points
        that have an ERROR > average error (not signal)

        These are points where the smoothing was poor
        """
        condition = np.abs(self.errors.values) > self.error_mean
        xnew = self.raw.times[condition]
        ynew = self.raw.values[condition]
        return TimeSeries(xnew, ynew, self.raw.copc, self.raw.site)

    def region_above_error(self):
        """ return a TimeSeries that only has values that
        are (strictly) greater than the estimated noise floor """
        condition = np.abs(self.raw.values) > self.error_mean
        xnew = self.raw.times[condition]
        ynew = self.raw.values[condition]
        return TimeSeries(xnew, ynew, self.raw.copc, self.raw.site)

    def region_below_error(self):
        """ return a TimeSeries that only has values that
        are less than or equal to the estimated noise floor """
        condition = np.abs(self.raw.values) <= self.error_mean
        xnew = self.raw.times[condition]
        ynew = self.raw.values[condition]
        return TimeSeries(xnew, ynew, self.raw.copc, self.raw.site)

